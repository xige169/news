from pathlib import Path
from datetime import datetime
from types import SimpleNamespace
import json
import sys

import pytest
from fastapi import HTTPException


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import backend.routers.comment as comment_router
import backend.routers.admin as admin_router
from backend.schemas.comment import CommentCreateRequest, CommentLikeRequest


def _make_user(user_id: int = 7, nickname: str | None = "小王", username: str = "wang", avatar: str | None = "u.png", role: str = "user"):
    return SimpleNamespace(id=user_id, nickname=nickname, username=username, avatar=avatar, role=role)


@pytest.mark.asyncio
async def test_add_comment_returns_serialized_payload(monkeypatch):
    async def fake_add_comment(db, *, user_id, news_id, content, parent_id):
        return SimpleNamespace(
            id=11,
            news_id=news_id,
            user_id=user_id,
            parent_id=parent_id,
            content=content,
            like_count=0,
            is_deleted=False,
            created_at=datetime(2026, 5, 10, 9, 0, 0),
        )

    monkeypatch.setattr(comment_router.comment_crud, "add_comment", fake_add_comment)

    response = await comment_router.add_comment(
        CommentCreateRequest(newsId=1, content="  hello  ", parentId=None),
        user=_make_user(),
        db=object(),
    )
    body = json.loads(response.body)
    assert body["code"] == 200
    assert body["message"] == "评论发表成功"
    assert body["data"]["id"] == 11
    assert body["data"]["newsId"] == 1
    assert body["data"]["userName"] == "小王"
    assert body["data"]["content"] == "hello"
    assert body["data"]["liked"] is False
    assert body["data"]["replies"] == []


@pytest.mark.asyncio
async def test_list_comments_anonymous_user_returns_tree(monkeypatch):
    async def fake_list_top_level_ids(db, news_id, page, page_size):
        return [1], 1

    async def fake_fetch_thread_rows(db, root_ids, current_user_id):
        assert current_user_id is None
        c1 = SimpleNamespace(
            id=1, news_id=5, user_id=7, parent_id=None,
            content="hi", like_count=2, is_deleted=False,
            created_at=datetime(2026, 5, 10, 8, 0, 0),
        )
        c2 = SimpleNamespace(
            id=2, news_id=5, user_id=8, parent_id=1,
            content="reply", like_count=0, is_deleted=False,
            created_at=datetime(2026, 5, 10, 8, 5, 0),
        )
        return [(c1, "alice", "a.png", False), (c2, "bob", "b.png", False)]

    monkeypatch.setattr(comment_router.comment_crud, "list_top_level_ids", fake_list_top_level_ids)
    monkeypatch.setattr(comment_router.comment_crud, "fetch_thread_rows", fake_fetch_thread_rows)

    response = await comment_router.list_comments(
        news_id=5, page=1, page_size=20,
        current_user=None,
        db=object(),
    )
    body = json.loads(response.body)
    assert body["code"] == 200
    assert body["data"]["total"] == 1
    assert body["data"]["hasMore"] is False
    top = body["data"]["list"][0]
    assert top["id"] == 1
    assert top["liked"] is False
    assert len(top["replies"]) == 1
    assert top["replies"][0]["id"] == 2
    assert top["replies"][0]["parentId"] == 1


@pytest.mark.asyncio
async def test_list_comments_logged_in_user_sees_liked_flag(monkeypatch):
    async def fake_list_top_level_ids(db, news_id, page, page_size):
        return [1], 1

    async def fake_fetch_thread_rows(db, root_ids, current_user_id):
        assert current_user_id == 7
        c1 = SimpleNamespace(
            id=1, news_id=5, user_id=8, parent_id=None,
            content="hi", like_count=3, is_deleted=False,
            created_at=datetime(2026, 5, 10, 8, 0, 0),
        )
        return [(c1, "alice", "a.png", True)]

    monkeypatch.setattr(comment_router.comment_crud, "list_top_level_ids", fake_list_top_level_ids)
    monkeypatch.setattr(comment_router.comment_crud, "fetch_thread_rows", fake_fetch_thread_rows)

    response = await comment_router.list_comments(
        news_id=5, page=1, page_size=20,
        current_user=_make_user(7),
        db=object(),
    )
    body = json.loads(response.body)
    assert body["data"]["list"][0]["liked"] is True


@pytest.mark.asyncio
async def test_list_comments_marks_deleted_node(monkeypatch):
    async def fake_list_top_level_ids(db, news_id, page, page_size):
        return [1], 1

    async def fake_fetch_thread_rows(db, root_ids, current_user_id):
        c1 = SimpleNamespace(
            id=1, news_id=5, user_id=8, parent_id=None,
            content="", like_count=0, is_deleted=True,
            created_at=datetime(2026, 5, 10, 8, 0, 0),
        )
        return [(c1, "alice", "a.png", False)]

    monkeypatch.setattr(comment_router.comment_crud, "list_top_level_ids", fake_list_top_level_ids)
    monkeypatch.setattr(comment_router.comment_crud, "fetch_thread_rows", fake_fetch_thread_rows)

    response = await comment_router.list_comments(
        news_id=5, page=1, page_size=20, current_user=None, db=object()
    )
    top = json.loads(response.body)["data"]["list"][0]
    assert top["isDeleted"] is True
    assert top["userId"] is None
    assert top["userName"] is None
    assert top["content"] == ""


@pytest.mark.asyncio
async def test_delete_comment_owner_succeeds(monkeypatch):
    async def fake_delete(db, user_id, comment_id):
        assert user_id == 7 and comment_id == 11
        return "ok"

    monkeypatch.setattr(comment_router.comment_crud, "delete_own_comment", fake_delete)

    response = await comment_router.delete_comment(11, user=_make_user(7), db=object())
    body = json.loads(response.body)
    assert body == {"code": 200, "message": "删除评论成功", "data": None}


@pytest.mark.asyncio
async def test_delete_comment_non_owner_forbidden(monkeypatch):
    async def fake_delete(db, user_id, comment_id):
        return "forbidden"

    monkeypatch.setattr(comment_router.comment_crud, "delete_own_comment", fake_delete)

    with pytest.raises(HTTPException) as exc:
        await comment_router.delete_comment(11, user=_make_user(7), db=object())
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_delete_comment_not_found(monkeypatch):
    async def fake_delete(db, user_id, comment_id):
        return "not_found"

    monkeypatch.setattr(comment_router.comment_crud, "delete_own_comment", fake_delete)

    with pytest.raises(HTTPException) as exc:
        await comment_router.delete_comment(11, user=_make_user(7), db=object())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_like_comment_returns_count_and_liked(monkeypatch):
    async def fake_toggle(db, user_id, comment_id, like):
        assert user_id == 7 and comment_id == 11 and like is True
        return 5, True

    monkeypatch.setattr(comment_router.comment_crud, "toggle_like", fake_toggle)

    response = await comment_router.like_comment(
        11, CommentLikeRequest(like=True), user=_make_user(7), db=object()
    )
    body = json.loads(response.body)
    assert body["data"] == {"commentId": 11, "likeCount": 5, "liked": True}


@pytest.mark.asyncio
async def test_admin_list_comments_returns_envelope(monkeypatch):
    async def fake_admin_list(db, *, keyword, news_id, page, page_size):
        assert keyword == "x" and news_id == 1
        return [
            {
                "id": 1,
                "newsId": 1,
                "newsTitle": "title",
                "userId": 8,
                "userName": "bob",
                "parentId": None,
                "content": "spam",
                "likeCount": 0,
                "isDeleted": False,
                "createdAt": "2026-05-10T08:00:00",
            }
        ], 1

    monkeypatch.setattr(admin_router.admin_comment, "admin_list_comments", fake_admin_list)

    response = await admin_router.get_admin_comments(
        page=1, page_size=20, keyword="x", news_id=1,
        db=object(), admin_user=_make_user(role="admin"),
    )
    body = json.loads(response.body)
    assert body["data"]["total"] == 1
    assert body["data"]["hasMore"] is False
    assert body["data"]["list"][0]["userName"] == "bob"


@pytest.mark.asyncio
async def test_admin_delete_comment_succeeds(monkeypatch):
    async def fake_admin_delete(db, comment_id):
        assert comment_id == 22
        return "ok"

    monkeypatch.setattr(admin_router.admin_comment, "admin_delete_comment", fake_admin_delete)

    response = await admin_router.delete_admin_comment(
        22, db=object(), admin_user=_make_user(role="admin")
    )
    body = json.loads(response.body)
    assert body == {"code": 200, "message": "删除评论成功", "data": None}


@pytest.mark.asyncio
async def test_admin_delete_comment_not_found(monkeypatch):
    async def fake_admin_delete(db, comment_id):
        return "not_found"

    monkeypatch.setattr(admin_router.admin_comment, "admin_delete_comment", fake_admin_delete)

    with pytest.raises(HTTPException) as exc:
        await admin_router.delete_admin_comment(
            22, db=object(), admin_user=_make_user(role="admin")
        )
    assert exc.value.status_code == 404


def test_build_tree_orders_by_top_ids():
    from backend.crud.comment import build_tree

    c1 = SimpleNamespace(id=1, news_id=5, user_id=7, parent_id=None, content="a",
                         like_count=0, is_deleted=False, created_at=datetime(2026, 5, 10, 8, 0))
    c2 = SimpleNamespace(id=2, news_id=5, user_id=8, parent_id=None, content="b",
                         like_count=0, is_deleted=False, created_at=datetime(2026, 5, 10, 8, 1))
    c3 = SimpleNamespace(id=3, news_id=5, user_id=9, parent_id=2, content="c",
                         like_count=0, is_deleted=False, created_at=datetime(2026, 5, 10, 8, 2))
    rows = [(c1, "u1", "a", False), (c2, "u2", "b", False), (c3, "u3", "c", False)]
    tree = build_tree([2, 1], rows)
    assert [n["id"] for n in tree] == [2, 1]
    assert [r["id"] for r in tree[0]["replies"]] == [3]
    assert tree[1]["replies"] == []
