from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.models.news import News


def test_news_model_matches_news_table_core_fields():
    table = News.__table__

    assert News.__tablename__ == "news"
    assert table.c.id.primary_key is True
    assert table.c.title.nullable is False
    assert table.c.description.nullable is True
    assert table.c.content.nullable is False
    assert table.c.category_id.nullable is False
    assert table.c.views.default.arg == 0
    assert table.c.status.nullable is False
    assert table.c.status.default.arg == "published"
    assert table.c.is_featured.nullable is False
    assert table.c.is_featured.default.arg is False
    assert "news_category.id" in str(next(iter(table.c.category_id.foreign_keys)).target_fullname)


def test_news_model_declares_expected_indexes():
    indexes = {index.name for index in News.__table__.indexes}

    assert "fk_news_category_idx" in indexes
    assert "idx_publish_time" in indexes
