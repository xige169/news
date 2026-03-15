from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.models.favorite import Favorite


def test_favorite_model_matches_favorite_table_core_fields():
    table = Favorite.__table__

    assert Favorite.__tablename__ == "favorite"
    assert table.c.id.primary_key is True
    assert table.c.user_id.nullable is False
    assert table.c.news_id.nullable is False
    assert table.c.created_at.nullable is False


def test_favorite_model_declares_expected_indexes_and_foreign_keys():
    table = Favorite.__table__
    indexes = {index.name for index in table.indexes}
    user_fk = next(iter(table.c.user_id.foreign_keys))
    news_fk = next(iter(table.c.news_id.foreign_keys))

    assert "user_news_unique" in indexes
    assert "fk_favorite_user_idx" in indexes
    assert "fk_favorite_news_idx" in indexes
    assert user_fk.target_fullname == "user.id"
    assert news_fk.target_fullname == "news.id"
