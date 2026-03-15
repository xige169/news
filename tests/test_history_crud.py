from pathlib import Path
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.crud.history import delete_one_history


class DummyResult:
    rowcount = 1


class DummySession:
    def __init__(self):
        self.statement = None
        self.committed = False

    async def execute(self, statement):
        self.statement = statement
        return DummyResult()

    async def commit(self):
        self.committed = True


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
