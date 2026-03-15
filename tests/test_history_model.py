from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.models.history import History


def test_history_model_matches_history_table_core_fields():
    table = History.__table__

    assert History.__tablename__ == "history"
    assert table.c.id.primary_key is True
    assert table.c.user_id.nullable is False
    assert table.c.news_id.nullable is False
    assert table.c.view_time.nullable is False


def test_history_model_declares_expected_indexes_and_foreign_keys():
    table = History.__table__
    indexes = {index.name for index in table.indexes}
    user_fk = next(iter(table.c.user_id.foreign_keys))
    news_fk = next(iter(table.c.news_id.foreign_keys))

    assert "fk_history_user_idx" in indexes
    assert "fk_history_news_idx" in indexes
    assert "idx_view_time" in indexes
    assert user_fk.target_fullname == "user.id"
    assert news_fk.target_fullname == "news.id"
