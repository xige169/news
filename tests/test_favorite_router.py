from pathlib import Path
from datetime import datetime
from types import SimpleNamespace
import json
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import backend.routers.favorite as favorite_router
from backend.schemas.favorite import FavoriteAddResponse


@pytest.mark.asyncio
async def test_add_favorite_accepts_news_id_alias_and_returns_success_payload(monkeypatch):
    async def fake_add_news_favorite(news_id: int, user_id: int, db):
        return SimpleNamespace(id=12, user_id=user_id, news_id=news_id)

    monkeypatch.setattr(favorite_router.favorite_crud, "add_news_favorite", fake_add_news_favorite)

    response = await favorite_router.add_favorite(
        FavoriteAddResponse(newsId=3),
        user=SimpleNamespace(id=7),
        db=object()
    )

    assert json.loads(response.body) == {
        "code": 200,
        "message": "收藏成功",
        "data": {
            "id": 12,
            "user_id": 7,
            "news_id": 3
        }
    }


@pytest.mark.asyncio
async def test_clear_favorite_list_awaits_crud_and_returns_deleted_count(monkeypatch):
    async def fake_clear_favorite_list(db, user_id: int):
        return 3

    monkeypatch.setattr(favorite_router.favorite_crud, "clear_favorite_list", fake_clear_favorite_list)

    response = await favorite_router.clear_favorite_list(
        user=SimpleNamespace(id=7),
        db=object()
    )

    assert json.loads(response.body) == {
        "code": 200,
        "message": "清空了3条记录",
        "data": None
    }


@pytest.mark.asyncio
async def test_get_favorite_list_returns_expected_payload(monkeypatch):
    async def fake_get_favorite_list(db, page: int, page_size: int, user_id: int):
        rows = [
            (
                SimpleNamespace(
                    id=5,
                    title="测试收藏新闻",
                    description="收藏简介",
                    image="https://example.com/favorite.jpg",
                    author="作者",
                    category_id=2,
                    views=99,
                    publish_time=datetime(2026, 3, 10, 8, 0, 0)
                ),
                datetime(2026, 3, 14, 10, 0, 0),
                42
            )
        ]
        return rows, 1

    monkeypatch.setattr(favorite_router.favorite_crud, "get_favorite_list", fake_get_favorite_list)

    response = await favorite_router.get_favorite_list(
        page=1,
        page_size=10,
        user=SimpleNamespace(id=7),
        db=object()
    )

    assert json.loads(response.body) == {
        "code": 200,
        "message": "获取收藏列表成功",
        "data": {
            "list": [
                {
                    "id": 5,
                    "title": "测试收藏新闻",
                    "description": "收藏简介",
                    "image": "https://example.com/favorite.jpg",
                    "author": "作者",
                    "categoryId": 2,
                    "views": 99,
                    "publishTime": "2026-03-10T08:00:00",
                    "favoriteId": 42,
                    "favoriteTime": "2026-03-14T10:00:00"
                }
            ],
            "total": 1,
            "hasMore": False
        }
    }
