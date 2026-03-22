from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.models.users import User, UserToken


def test_user_model_matches_user_table_core_fields():
    table = User.__table__

    assert User.__tablename__ == "user"
    assert table.c.id.primary_key is True
    assert table.c.username.nullable is False
    assert table.c.password.nullable is False
    assert table.c.nickname.nullable is True
    assert table.c.gender.default.arg == "unknown"
    assert table.c.phone.nullable is True
    assert table.c.role.nullable is False
    assert table.c.role.default.arg == "user"


def test_user_model_declares_expected_indexes():
    indexes = {index.name for index in User.__table__.indexes}

    assert "username_UNIQUE" in indexes
    assert "phone_UNIQUE" in indexes


def test_user_token_model_matches_table_constraints():
    table = UserToken.__table__
    foreign_key = next(iter(table.c.user_id.foreign_keys))

    assert UserToken.__tablename__ == "user_token"
    assert table.c.user_id.nullable is False
    assert table.c.token.nullable is False
    assert table.c.expires_at.nullable is False
    assert foreign_key.target_fullname == "user.id"


def test_user_token_model_declares_expected_indexes():
    indexes = {index.name for index in UserToken.__table__.indexes}

    assert "token_UNIQUE" in indexes
    assert "fk_user_token_user_idx" in indexes
