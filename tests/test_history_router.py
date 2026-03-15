from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import json
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.routers.history import add_history, clear_history, delete_one_history, get_history_list
from backend.schemas.history import HistoryAddRequest


@pytest.mark.asyncio
async def test_add_history_returns_expected_payload(monkeypatch):
    recorded = {}

    async def fake_add_news_history(news_id: int, user_id: int, db):
        recorded["news_id"] = news_id
        recorded["user_id"] = user_id
        recorded["db"] = db
        return SimpleNamespace(
            id=11,
            user_id=user_id,
            news_id=news_id,
            view_time=datetime(2026, 3, 14, 9, 30, 0)
        )

    monkeypatch.setattr("backend.routers.history.history.add_news_history", fake_add_news_history)

    response = await add_history(
        HistoryAddRequest(newsId=3),
        user=SimpleNamespace(id=7),
        db=object()
    )

    assert recorded == {
        "news_id": 3,
        "user_id": 7,
        "db": recorded["db"]
    }
    assert json.loads(response.body) == {
        "code": 200,
        "message": "添加成功",
        "data": {
            "id": 11,
            "userId": 7,
            "newsId": 3,
            "viewTime": "2026-03-14T09:30:00"
        }
    }


@pytest.mark.asyncio
async def test_get_history_list_returns_expected_payload(monkeypatch):
    recorded = {}

    async def fake_get_history_list(db, user_id: int, page: int, page_size: int):
        recorded["db"] = db
        recorded["user_id"] = user_id
        recorded["page"] = page
        recorded["page_size"] = page_size
        rows = [
            (
                SimpleNamespace(
                    id=5,
                    title="测试新闻",
                    description="简介",
                    image="https://example.com/image.jpg",
                    author="作者",
                    category_id=2,
                    views=99,
                    publish_time=datetime(2026, 3, 10, 8, 0, 0)
                ),
                datetime(2026, 3, 14, 10, 0, 0)
            )
        ]
        return rows, 1

    monkeypatch.setattr("backend.routers.history.history.get_history_list", fake_get_history_list)

    response = await get_history_list(
        page=1,
        page_size=10,
        user=SimpleNamespace(id=7),
        db=object()
    )

    assert recorded["user_id"] == 7
    assert recorded["page"] == 1
    assert recorded["page_size"] == 10
    assert json.loads(response.body) == {
        "code": 200,
        "message": "获取成功",
        "data": {
            "list": [
                {
                    "id": 5,
                    "title": "测试新闻",
                    "description": "简介",
                    "image": "https://example.com/image.jpg",
                    "author": "作者",
                    "categoryId": 2,
                    "views": 99,
                    "publishTime": "2026-03-10T08:00:00",
                    "viewTime": "2026-03-14T10:00:00"
                }
            ],
            "total": 1,
            "hasMore": False
        }
    }


@pytest.mark.asyncio
async def test_delete_one_history_returns_success_payload(monkeypatch):
    recorded = {}

    async def fake_delete_one_history(history_id: int, user_id: int, db):
        recorded["history_id"] = history_id
        recorded["user_id"] = user_id
        recorded["db"] = db
        return True

    monkeypatch.setattr("backend.routers.history.history.delete_one_history", fake_delete_one_history)

    response = await delete_one_history(
        history_id=11,
        user=SimpleNamespace(id=7),
        db=object()
    )

    assert recorded["history_id"] == 11
    assert recorded["user_id"] == 7
    assert json.loads(response.body) == {
        "code": 200,
        "message": "删除成功",
        "data": None
    }


@pytest.mark.asyncio
async def test_clear_history_returns_success_payload_when_rows_deleted(monkeypatch):
    recorded = {}

    async def fake_clear_history(user_id: int, db):
        recorded["user_id"] = user_id
        recorded["db"] = db
        return 3

    monkeypatch.setattr("backend.routers.history.history.clear_history", fake_clear_history)

    response = await clear_history(
        user=SimpleNamespace(id=7),
        db=object()
    )

    assert recorded["user_id"] == 7
    assert json.loads(response.body) == {
        "code": 200,
        "message": "清空成功",
        "data": None
    }


@pytest.mark.asyncio
async def test_clear_history_returns_success_payload_when_list_already_empty(monkeypatch):
    async def fake_clear_history(user_id: int, db):
        return 0

    monkeypatch.setattr("backend.routers.history.history.clear_history", fake_clear_history)

    response = await clear_history(
        user=SimpleNamespace(id=7),
        db=object()
    )

    assert json.loads(response.body) == {
        "code": 200,
        "message": "清空成功",
        "data": None
    }
