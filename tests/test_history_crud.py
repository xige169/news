from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.crud.history import add_news_history, delete_one_history


class DummyResult:
    def __init__(self, rowcount=1, scalar=None):
        self.rowcount = rowcount
        self._scalar = scalar

    def scalar_one_or_none(self):
        return self._scalar


class DummySession:
    def __init__(self):
        self.statement = None
        self.committed = False
        self.added = []
        self.refreshed = []
        self.scalar = None

    async def execute(self, statement):
        self.statement = statement
        return DummyResult(scalar=self.scalar)

    def add(self, value):
        self.added.append(value)

    async def commit(self):
        self.committed = True

    async def refresh(self, value):
        self.refreshed.append(value)


class DummyHistoryListResult:
    def __init__(self, scalar=None, rows=None):
        self._scalar = scalar
        self._rows = rows or []

    def scalar_one(self):
        return self._scalar

    def all(self):
        return self._rows


class DummyHistoryListSession:
    def __init__(self):
        self.statements = []

    async def execute(self, statement):
        self.statements.append(statement)
        if len(self.statements) == 1:
            return DummyHistoryListResult(scalar=1)
        return DummyHistoryListResult(rows=[])


@pytest.mark.asyncio
async def test_add_news_history_reuses_existing_history_for_same_user_and_news():
    session = DummySession()
    existing = SimpleNamespace(
        id=9,
        user_id=7,
        news_id=3,
        view_time=datetime(2026, 3, 10, 8, 0, 0)
    )
    session.scalar = existing

    history = await add_news_history(news_id=3, user_id=7, db=session)

    where_sql = str(session.statement.whereclause)

    assert history is existing
    assert history.view_time != datetime(2026, 3, 10, 8, 0, 0)
    assert session.added == []
    assert session.refreshed == []
    assert session.committed is True
    assert "history.user_id" in where_sql
    assert "history.news_id" in where_sql


@pytest.mark.asyncio
async def test_delete_one_history_deletes_by_history_id_for_current_user():
    session = DummySession()

    deleted = await delete_one_history(history_id=11, user_id=7, db=session)

    where_sql = str(session.statement.whereclause)

    assert deleted is True
    assert session.committed is True
    assert "history.user_id" in where_sql
    assert "history.id" in where_sql
    assert "history.news_id" not in where_sql


@pytest.mark.asyncio
async def test_get_history_list_uses_same_latest_row_for_history_id_and_view_time():
    session = DummyHistoryListSession()

    from backend.crud.history import get_history_list

    await get_history_list(db=session, user_id=7, page=1, page_size=10)

    count_sql = str(session.statements[0])
    list_sql = str(session.statements[1])

    assert "row_number()" in count_sql.lower()
    assert "row_number()" in list_sql.lower()
    assert "PARTITION BY history.news_id" in list_sql
    assert "ORDER BY history.view_time DESC, history.id DESC" in list_sql
