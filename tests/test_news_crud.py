from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.crud.news import (
    get_categories,
    get_news_count,
    get_news_detail,
    get_hot_news,
    get_news_list,
    get_personalized_news,
    get_news_recommend,
    search_news,
    update_news_views,
)
from backend.cache.news_cache import get_news_list_cache
from backend.schemas.base import NewsItemBase


class DummyResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def all(self):
        return self._rows

    def scalar_one(self):
        return self._rows

    def scalar_one_or_none(self):
        return self._rows


class DummySession:
    def __init__(self, rows):
        self.rows = rows
        self.execute_called = False
        self.statement = None
        self.committed = False

    async def execute(self, statement):
        self.execute_called = True
        self.statement = statement
        return DummyResult(self.rows)

    async def commit(self):
        self.committed = True


class DummyUpdateResult:
    def __init__(self, rowcount):
        self.rowcount = rowcount


class DummyUpdateSession:
    def __init__(self, category_id: int | None, rowcount: int = 1):
        self.category_id = category_id
        self.rowcount = rowcount
        self.statements = []
        self.committed = False

    async def execute(self, statement):
        self.statements.append(statement)
        if len(self.statements) == 1:
            return DummyResult(self.category_id)
        return DummyUpdateResult(self.rowcount)

    async def commit(self):
        self.committed = True


class DummyMultiExecuteSession:
    def __init__(self, rows):
        self.rows = list(rows)
        self.statements = []

    async def execute(self, statement):
        self.statements.append(statement)
        return DummyResult(self.rows.pop(0))


@pytest.mark.asyncio
async def test_get_news_list_uses_cache_before_database(monkeypatch):
    cached_rows = [
        {
            "id": 1,
            "title": "缓存新闻",
            "description": "来自缓存",
            "content": "content",
            "image": "https://example.com/cached.jpg",
            "author": "tester",
            "category_id": 2,
            "views": 120,
            "status": "published",
            "publish_time": "2026-03-14T09:00:00",
        }
    ]

    async def fake_get_news_list_cache(category_id: int, page: int, page_size: int):
        assert category_id == 2
        assert page == 3
        assert page_size == 10
        return cached_rows

    async def fake_set_news_list_cache(*args, **kwargs):
        raise AssertionError("缓存命中时不应回填缓存")

    monkeypatch.setattr("backend.crud.news.news_cache.get_news_list_cache", fake_get_news_list_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_news_list_cache", fake_set_news_list_cache)

    session = DummySession(rows=[])

    result = await get_news_list(session, category_id=2, skip=20, limit=10)

    assert session.execute_called is False
    assert len(result) == 1
    assert isinstance(result[0], NewsItemBase)
    assert result[0].title == "缓存新闻"
    assert result[0].category_id == 2


@pytest.mark.asyncio
async def test_get_categories_uses_cache_before_database(monkeypatch):
    cached_rows = [{"id": 1, "name": "要闻", "sort_order": 1}]

    async def fake_get_categories_cache():
        return cached_rows

    async def fake_set_categories_cache(*args, **kwargs):
        raise AssertionError("分类缓存命中时不应回填")

    monkeypatch.setattr("backend.crud.news.news_cache.get_categories_cache", fake_get_categories_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_categories_cache", fake_set_categories_cache)

    session = DummySession(rows=[])

    result = await get_categories(session)

    assert result == cached_rows
    assert session.execute_called is False


@pytest.mark.asyncio
async def test_get_news_list_returns_cached_empty_page_without_querying_database(monkeypatch):
    async def fake_get_news_list_cache(category_id: int, page: int, page_size: int):
        assert category_id == 2
        assert page == 1
        assert page_size == 10
        return []

    async def fake_set_news_list_cache(*args, **kwargs):
        raise AssertionError("空页已被缓存时不应再次回填")

    monkeypatch.setattr("backend.crud.news.news_cache.get_news_list_cache", fake_get_news_list_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_news_list_cache", fake_set_news_list_cache)

    session = DummySession(rows=["unexpected"])

    result = await get_news_list(session, category_id=2, skip=0, limit=10)

    assert result == []
    assert session.execute_called is False


@pytest.mark.asyncio
async def test_get_news_list_populates_cache_after_database_query(monkeypatch):
    cached = {"called": False}

    async def fake_get_news_list_cache(category_id: int, page: int, page_size: int):
        assert category_id == 3
        assert page == 1
        assert page_size == 10
        return None

    async def fake_set_news_list_cache(category_id: int, page: int, page_size: int, data, expire: int = 1800):
        cached["called"] = True
        cached["category_id"] = category_id
        cached["page"] = page
        cached["page_size"] = page_size
        cached["data"] = data
        cached["expire"] = expire
        return True

    monkeypatch.setattr("backend.crud.news.news_cache.get_news_list_cache", fake_get_news_list_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_news_list_cache", fake_set_news_list_cache)

    rows = [
        SimpleNamespace(
            id=8,
            title="数据库新闻",
            description="来自数据库",
            content="content",
            image="https://example.com/db.jpg",
            author="tester",
            category_id=3,
            views=9,
            publish_time=datetime(2026, 3, 14, 8, 30, 0),
        )
    ]
    session = DummySession(rows=rows)

    result = await get_news_list(session, category_id=3, skip=0, limit=10)

    assert session.execute_called is True
    assert cached["called"] is True
    assert cached["category_id"] == 3
    assert cached["page"] == 1
    assert cached["page_size"] == 10
    assert cached["expire"] == 1800
    assert cached["data"][0]["title"] == "数据库新闻"
    assert isinstance(result[0], NewsItemBase)
    assert result[0].title == "数据库新闻"


@pytest.mark.asyncio
async def test_get_news_list_only_queries_published_news(monkeypatch):
    async def fake_get_news_list_cache(category_id: int, page: int, page_size: int):
        return None

    async def fake_set_news_list_cache(*args, **kwargs):
        return True

    monkeypatch.setattr("backend.crud.news.news_cache.get_news_list_cache", fake_get_news_list_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_news_list_cache", fake_set_news_list_cache)

    session = DummySession(rows=[])

    await get_news_list(session, category_id=3, skip=0, limit=10)

    compiled = session.statement.compile()
    assert compiled.params["category_id_1"] == 3
    assert compiled.params["status_1"] == "published"


@pytest.mark.asyncio
async def test_get_news_list_cache_returns_cached_payload(monkeypatch):
    async def fake_get_json_cache(key: str):
        assert key == "news:list:5:2:10"
        return [{"id": 99, "title": "缓存已返回"}]

    monkeypatch.setattr("backend.cache.news_cache.cache_conf.get_json_cache", fake_get_json_cache)

    result = await get_news_list_cache(category_id=5, page=2, page_size=10)

    assert result == [{"id": 99, "title": "缓存已返回"}]


@pytest.mark.asyncio
async def test_get_news_count_uses_cache_before_database(monkeypatch):
    async def fake_get_news_count_cache(category_id: int):
        assert category_id == 7
        return 33

    async def fake_set_news_count_cache(*args, **kwargs):
        raise AssertionError("数量缓存命中时不应回填")

    monkeypatch.setattr("backend.crud.news.news_cache.get_news_count_cache", fake_get_news_count_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_news_count_cache", fake_set_news_count_cache)

    session = DummySession(rows=0)

    result = await get_news_count(session, category_id=7)

    assert result == 33
    assert session.execute_called is False


@pytest.mark.asyncio
async def test_get_news_count_populates_cache_after_database_query(monkeypatch):
    cached = {}

    async def fake_get_news_count_cache(category_id: int):
        return None

    async def fake_set_news_count_cache(category_id: int, count: int, expire: int = 1800):
        cached["category_id"] = category_id
        cached["count"] = count
        cached["expire"] = expire
        return True

    monkeypatch.setattr("backend.crud.news.news_cache.get_news_count_cache", fake_get_news_count_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_news_count_cache", fake_set_news_count_cache)

    session = DummySession(rows=12)

    result = await get_news_count(session, category_id=5)

    assert result == 12
    assert session.execute_called is True
    assert cached == {"category_id": 5, "count": 12, "expire": 1800}


@pytest.mark.asyncio
async def test_get_news_detail_uses_cache_before_database(monkeypatch):
    cached_row = {
        "id": 9,
        "title": "缓存详情",
        "description": "来自缓存",
        "content": "detail",
        "image": "https://example.com/detail.jpg",
        "author": "tester",
        "category_id": 4,
        "views": 88,
        "status": "published",
        "publish_time": "2026-03-14T09:00:00",
    }

    async def fake_get_news_detail_cache(news_id: int):
        assert news_id == 9
        return cached_row

    async def fake_set_news_detail_cache(*args, **kwargs):
        raise AssertionError("详情缓存命中时不应回填")

    monkeypatch.setattr("backend.crud.news.news_cache.get_news_detail_cache", fake_get_news_detail_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_news_detail_cache", fake_set_news_detail_cache)

    session = DummySession(rows=None)

    result = await get_news_detail(session, news_id=9)

    assert session.execute_called is False
    assert result.id == 9
    assert result.title == "缓存详情"
    assert result.category_id == 4


@pytest.mark.asyncio
async def test_get_news_detail_populates_cache_after_database_query(monkeypatch):
    cached = {}

    async def fake_get_news_detail_cache(news_id: int):
        return None

    async def fake_set_news_detail_cache(news_id: int, data, expire: int = 3600):
        cached["news_id"] = news_id
        cached["data"] = data
        cached["expire"] = expire
        return True

    monkeypatch.setattr("backend.crud.news.news_cache.get_news_detail_cache", fake_get_news_detail_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_news_detail_cache", fake_set_news_detail_cache)

    session = DummySession(
        rows=SimpleNamespace(
            id=6,
            title="数据库详情",
            description="来自数据库",
            content="detail",
            image="https://example.com/detail.jpg",
            author="tester",
            category_id=2,
            views=18,
            publish_time=datetime(2026, 3, 14, 7, 30, 0),
        )
    )

    result = await get_news_detail(session, news_id=6)

    assert session.execute_called is True
    assert result.id == 6
    assert cached["news_id"] == 6
    assert cached["expire"] == 3600
    assert cached["data"]["title"] == "数据库详情"


@pytest.mark.asyncio
async def test_get_news_detail_only_queries_published_news_when_cache_misses(monkeypatch):
    async def fake_get_news_detail_cache(news_id: int):
        return None

    async def fake_set_news_detail_cache(*args, **kwargs):
        return True

    monkeypatch.setattr("backend.crud.news.news_cache.get_news_detail_cache", fake_get_news_detail_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_news_detail_cache", fake_set_news_detail_cache)

    session = DummySession(rows=None)

    await get_news_detail(session, news_id=6)

    compiled = session.statement.compile()
    assert compiled.params["id_1"] == 6
    assert compiled.params["status_1"] == "published"


@pytest.mark.asyncio
async def test_get_news_recommend_uses_cache_before_database(monkeypatch):
    cached_rows = [{"id": 2, "title": "缓存推荐", "publishTime": "2026-03-14T09:00:00", "categoryId": 3, "views": 10, "status": "published"}]

    async def fake_get_news_recommend_cache(category_id: int, news_id: int, limit: int):
        assert category_id == 3
        assert news_id == 1
        assert limit == 5
        return cached_rows

    async def fake_set_news_recommend_cache(*args, **kwargs):
        raise AssertionError("推荐缓存命中时不应回填")

    monkeypatch.setattr("backend.crud.news.news_cache.get_news_recommend_cache", fake_get_news_recommend_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_news_recommend_cache", fake_set_news_recommend_cache)

    session = DummySession(rows=[])

    result = await get_news_recommend(session, news_id=1, category_id=3, limit=5)

    assert result == cached_rows
    assert session.execute_called is False


@pytest.mark.asyncio
async def test_get_news_recommend_populates_cache_after_database_query(monkeypatch):
    cached = {}

    async def fake_get_news_recommend_cache(category_id: int, news_id: int, limit: int):
        return None

    async def fake_set_news_recommend_cache(category_id: int, news_id: int, limit: int, data, expire: int = 1800):
        cached["category_id"] = category_id
        cached["news_id"] = news_id
        cached["limit"] = limit
        cached["data"] = data
        cached["expire"] = expire
        return True

    monkeypatch.setattr("backend.crud.news.news_cache.get_news_recommend_cache", fake_get_news_recommend_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.set_news_recommend_cache", fake_set_news_recommend_cache)

    session = DummySession(
        rows=[
            SimpleNamespace(
                id=7,
                title="数据库推荐",
                description="推荐摘要",
                content="content",
                image="https://example.com/recommend.jpg",
                author="tester",
                category_id=3,
                views=66,
                status="published",
                publish_time=datetime(2026, 3, 14, 6, 0, 0),
            )
        ]
    )

    result = await get_news_recommend(session, news_id=1, category_id=3, limit=5)

    assert session.execute_called is True
    assert result[0]["title"] == "数据库推荐"
    assert cached["category_id"] == 3
    assert cached["news_id"] == 1
    assert cached["limit"] == 5
    assert cached["expire"] == 1800


@pytest.mark.asyncio
async def test_search_news_only_returns_published_news():
    session = DummyMultiExecuteSession([[], 0])

    await search_news(session, keyword="AI", category_id=2, skip=0, limit=10)

    stmt_params = session.statements[0].compile().params
    count_params = session.statements[1].compile().params

    assert stmt_params["category_id_1"] == 2
    assert stmt_params["status_1"] == "published"
    assert count_params["status_1"] == "published"


@pytest.mark.asyncio
async def test_get_hot_news_only_returns_published_news():
    session = DummyMultiExecuteSession([[], 0])

    await get_hot_news(session, skip=0, limit=10)

    stmt_params = session.statements[0].compile().params
    count_params = session.statements[1].compile().params

    assert stmt_params["status_1"] == "published"
    assert count_params["status_1"] == "published"


@pytest.mark.asyncio
async def test_get_personalized_news_only_uses_published_candidates():
    session = DummyMultiExecuteSession([
        [(3, 11)],
        [(3, 12)],
        [],
        0,
    ])

    await get_personalized_news(session, user_id=7, skip=0, limit=10)

    candidate_params = session.statements[2].compile().params
    count_params = session.statements[3].compile().params

    assert candidate_params["status_1"] == "published"
    assert count_params["status_1"] == "published"


@pytest.mark.asyncio
async def test_update_news_views_invalidates_related_caches_after_database_update(monkeypatch):
    invalidation = {}

    async def fake_delete_news_detail_cache(news_id: int):
        invalidation["news_id"] = news_id
        return True

    async def fake_delete_news_list_cache(category_id: int):
        invalidation["list_category_id"] = category_id
        return True

    async def fake_delete_news_recommend_cache_by_category(category_id: int):
        invalidation["recommend_category_id"] = category_id
        return True

    monkeypatch.setattr("backend.crud.news.news_cache.delete_news_detail_cache", fake_delete_news_detail_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.delete_news_list_cache", fake_delete_news_list_cache)
    monkeypatch.setattr("backend.crud.news.news_cache.delete_news_recommend_cache_by_category", fake_delete_news_recommend_cache_by_category)

    session = DummyUpdateSession(category_id=4, rowcount=1)

    result = await update_news_views(session, news_id=11)

    assert result is True
    assert session.committed is True
    assert invalidation == {
        "news_id": 11,
        "list_category_id": 4,
        "recommend_category_id": 4,
    }
