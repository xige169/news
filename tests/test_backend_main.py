from pathlib import Path
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import backend.routers.news as news_router
from backend.main import app, root


@pytest.mark.asyncio
async def test_root_endpoint_returns_hello_world():
    assert await root() == {"message": "Hello World"}


@pytest.mark.asyncio
async def test_news_categories_endpoint_is_registered(monkeypatch):
    async def fake_get_categories(db, skip: int, limit: int):
        assert skip == 0
        assert limit == 100
        return [{"id": 1, "name": "要闻"}]

    monkeypatch.setattr("backend.routers.news.news.get_categories", fake_get_categories)

    route_paths = {route.path for route in app.routes}
    payload = await news_router.get_categories(db=object())

    assert "/api/news/categories" in route_paths
    assert payload == {
        "code": 200,
        "message": "success",
        "data": [{"id": 1, "name": "要闻"}]
    }


@pytest.mark.asyncio
async def test_news_search_endpoint_is_registered(monkeypatch):
    async def fake_search_news(db, keyword: str, category_id, skip: int, limit: int):
        assert keyword == "AI"
        assert category_id == 2
        assert skip == 10
        assert limit == 10
        return [{"id": 8, "title": "AI 快讯"}], 11

    monkeypatch.setattr("backend.routers.news.news.search_news", fake_search_news)

    route_paths = {route.path for route in app.routes}
    payload = await news_router.search_news_list(keyword="AI", category_id=2, page=2, pagesize=10, db=object())

    assert "/api/news/search" in route_paths
    assert payload == {
        "code": 200,
        "message": "success",
        "data": {
            "list": [{"id": 8, "title": "AI 快讯"}],
            "total": 11,
            "hasMore": False
        }
    }


@pytest.mark.asyncio
async def test_hot_news_endpoint_is_registered(monkeypatch):
    async def fake_get_hot_news(db, skip: int, limit: int):
        assert skip == 0
        assert limit == 5
        return [{"id": 3, "title": "热门新闻"}], 1

    monkeypatch.setattr("backend.routers.news.news.get_hot_news", fake_get_hot_news)

    route_paths = {route.path for route in app.routes}
    payload = await news_router.get_hot_news_list(page=1, pagesize=5, db=object())

    assert "/api/news/hot" in route_paths
    assert payload["data"]["list"][0]["title"] == "热门新闻"
    assert payload["data"]["hasMore"] is False


@pytest.mark.asyncio
async def test_recommend_news_endpoint_uses_hot_list_for_guests(monkeypatch):
    async def fake_get_hot_news(db, skip: int, limit: int):
        assert skip == 0
        assert limit == 6
        return [{"id": 9, "title": "游客推荐"}], 1

    monkeypatch.setattr("backend.routers.news.news.get_hot_news", fake_get_hot_news)

    payload = await news_router.get_recommend_news_list(page=1, pagesize=6, db=object())

    assert payload["data"]["list"][0]["title"] == "游客推荐"
    assert payload["data"]["source"] == "hot"


@pytest.mark.asyncio
async def test_recommend_news_endpoint_uses_personalized_list_for_login_user(monkeypatch):
    async def fake_get_personalized_news(db, user_id: int, skip: int, limit: int):
        assert user_id == 7
        assert skip == 6
        assert limit == 6
        return [{"id": 12, "title": "为你推荐"}], 20

    async def fake_get_current_user(authorization: str, db):
        assert authorization == "Bearer token"
        return type("User", (), {"id": 7})()

    monkeypatch.setattr("backend.routers.news.news.get_personalized_news", fake_get_personalized_news)
    monkeypatch.setattr("backend.routers.news.auth.get_current_user", fake_get_current_user)

    payload = await news_router.get_recommend_news_list(
        page=2,
        pagesize=6,
        db=object(),
        authorization="Bearer token"
    )

    assert payload["data"]["list"][0]["title"] == "为你推荐"
    assert payload["data"]["source"] == "personalized"
