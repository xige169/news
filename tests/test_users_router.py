from pathlib import Path
from datetime import datetime
from types import SimpleNamespace
import sys

import pytest
from fastapi import HTTPException


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.crud import users as users_crud
from backend.routers.users import login, register
from backend.schemas.users import UserRequest, UserUpdateRequest
from backend.utils import auth


@pytest.mark.asyncio
async def test_register_raises_http_exception_when_user_exists(monkeypatch):
    async def fake_get_user_by_username(username: str, db):
        return SimpleNamespace(id=1, username=username)

    monkeypatch.setattr("backend.routers.users.users.get_user_by_username", fake_get_user_by_username)

    with pytest.raises(HTTPException) as exc_info:
        await register(UserRequest(username="alice", password="secret"), db=object())

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "用户已存在"


@pytest.mark.asyncio
async def test_login_raises_http_exception_when_credentials_invalid(monkeypatch):
    async def fake_authenticate_user(username: str, password: str, db):
        return None

    monkeypatch.setattr("backend.routers.users.users.authenticate_user", fake_authenticate_user)

    with pytest.raises(HTTPException) as exc_info:
        await login(UserRequest(username="alice", password="bad-password"), db=object())

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "用户名或密码错误"


@pytest.mark.asyncio
async def test_get_current_user_raises_http_exception_when_token_invalid(monkeypatch):
    async def fake_get_user_by_token(token: str, db):
        return None

    monkeypatch.setattr("backend.utils.auth.users.get_user_by_token", fake_get_user_by_token)

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(authorization="Bearer invalid-token", db=object())

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "无效令牌或者令牌已过期"


@pytest.mark.asyncio
async def test_get_user_by_id_uses_requested_id_in_query():
    captured = {}

    class FakeResult:
        def scalar_one_or_none(self):
            return None

    class FakeDb:
        async def execute(self, stmt):
            compiled = stmt.compile()
            captured["params"] = compiled.params
            return FakeResult()

    await users_crud.get_user_by_id(7, FakeDb())

    assert captured["params"] == {"id_1": 7}


@pytest.mark.asyncio
async def test_get_current_user_raises_http_exception_when_authorization_header_malformed():
    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(authorization="invalid-token", db=object())

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "无效令牌或者令牌已过期"


@pytest.mark.asyncio
async def test_update_user_info_raises_http_exception_when_user_missing():
    class FakeResult:
        rowcount = 0

    class FakeDb:
        async def execute(self, stmt):
            return FakeResult()

        async def commit(self):
            return None

    with pytest.raises(HTTPException) as exc_info:
        await users_crud.update_user_info(UserUpdateRequest(nickname="new-name"), 9, FakeDb())

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "用户不存在"


@pytest.mark.asyncio
async def test_create_token_commits_when_existing_token_is_updated():
    existing_token = SimpleNamespace(
        user_id=7,
        token="old-token",
        expires_at=datetime(2026, 1, 1, 0, 0, 0)
    )
    committed = {"value": False}

    class FakeResult:
        def scalar_one_or_none(self):
            return existing_token

    class FakeDb:
        async def execute(self, stmt):
            return FakeResult()

        async def commit(self):
            committed["value"] = True

        async def refresh(self, instance):
            return None

        def add(self, instance):
            return None

    token = await users_crud.create_token(7, FakeDb())

    assert committed["value"] is True
    assert existing_token.token == token
