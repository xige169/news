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
