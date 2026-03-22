from pathlib import Path
from types import SimpleNamespace
import sys

import pytest
from fastapi import HTTPException


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.crud import users as users_crud
from backend.routers.users import login, logout, refresh_token, register
from backend.schemas.users import RefreshTokenRequest, UserRequest, UserUpdateRequest
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
    async def fake_get_user_by_id(user_id: int, db):
        raise AssertionError("无效 JWT 不应查询用户")

    monkeypatch.setattr("backend.utils.auth.users.get_user_by_id", fake_get_user_by_id)

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
async def test_create_token_returns_jwt_with_three_segments():
    token = await users_crud.create_token(7, object())

    assert len(token.split(".")) == 3


@pytest.mark.asyncio
async def test_get_current_user_accepts_valid_jwt_and_loads_user(monkeypatch):
    expected_user = SimpleNamespace(id=7, username="alice")

    async def fake_get_user_by_id(user_id: int, db):
        assert user_id == 7
        return expected_user

    monkeypatch.setattr("backend.utils.auth.users.get_user_by_id", fake_get_user_by_id)

    token = await users_crud.create_token(7, object())

    user = await auth.get_current_user(authorization=f"Bearer {token}", db=object())

    assert user is expected_user


@pytest.mark.asyncio
async def test_get_current_user_rejects_tampered_jwt(monkeypatch):
    async def fake_get_user_by_id(user_id: int, db):
        raise AssertionError("伪造 JWT 不应查询用户")

    monkeypatch.setattr("backend.utils.auth.users.get_user_by_id", fake_get_user_by_id)

    token = await users_crud.create_token(7, object())
    tampered_token = f"{token}tampered"

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_current_user(authorization=f"Bearer {tampered_token}", db=object())

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "无效令牌或者令牌已过期"


@pytest.mark.asyncio
async def test_login_returns_access_and_refresh_tokens(monkeypatch):
    async def fake_authenticate_user(username: str, password: str, db):
        return SimpleNamespace(id=5, username=username, nickname=None, avatar=None, gender="unknown", bio=None)

    async def fake_create_auth_tokens(user_id: int):
        assert user_id == 5
        return {
            "token": "access-token",
            "accessToken": "access-token",
            "refreshToken": "refresh-token",
        }

    monkeypatch.setattr("backend.routers.users.users.authenticate_user", fake_authenticate_user)
    monkeypatch.setattr("backend.routers.users.users.create_auth_tokens", fake_create_auth_tokens)

    response = await login(UserRequest(username="alice", password="secret"), db=object())

    assert response.body.decode("utf-8").count("refresh-token") == 1
    assert response.body.decode("utf-8").count("access-token") == 2


@pytest.mark.asyncio
async def test_refresh_token_returns_new_access_token_pair(monkeypatch):
    async def fake_refresh_auth_tokens(refresh_token: str, db):
        assert refresh_token == "valid-refresh"
        return {
            "token": "next-access",
            "accessToken": "next-access",
            "refreshToken": "next-refresh",
        }

    monkeypatch.setattr("backend.routers.users.users.refresh_auth_tokens", fake_refresh_auth_tokens)

    response = await refresh_token(RefreshTokenRequest(refreshToken="valid-refresh"), db=object())

    assert response.body.decode("utf-8").count("next-refresh") == 1
    assert response.body.decode("utf-8").count("next-access") == 2


@pytest.mark.asyncio
async def test_logout_blacklists_current_access_token(monkeypatch):
    async def fake_blacklist_token(token: str):
        assert token == "access-token"
        return True

    monkeypatch.setattr("backend.routers.users.auth.blacklist_token", fake_blacklist_token)

    response = await logout(
        authorization="Bearer access-token",
        user=SimpleNamespace(id=7),
    )

    assert response.body.decode("utf-8").count("退出登录成功") == 1
