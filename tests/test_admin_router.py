from pathlib import Path
from types import SimpleNamespace
import json
import sys

import pytest
from fastapi import HTTPException


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import backend.routers.admin as admin_router
from backend.utils import auth


@pytest.mark.asyncio
async def test_require_admin_user_returns_admin_user(monkeypatch):
    admin_user = SimpleNamespace(id=1, role='admin')

    async def fake_get_current_user(authorization: str, db):
        assert authorization == 'Bearer admin-token'
        return admin_user

    monkeypatch.setattr('backend.utils.auth.get_current_user', fake_get_current_user)

    user = await auth.require_admin_user(authorization='Bearer admin-token', db=object())

    assert user is admin_user


@pytest.mark.asyncio
async def test_require_admin_user_rejects_normal_user(monkeypatch):
    async def fake_get_current_user(authorization: str, db):
        return SimpleNamespace(id=2, role='user')

    monkeypatch.setattr('backend.utils.auth.get_current_user', fake_get_current_user)

    with pytest.raises(HTTPException) as exc_info:
        await auth.require_admin_user(authorization='Bearer user-token', db=object())

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == '没有管理员权限'


@pytest.mark.asyncio
async def test_admin_dashboard_summary_endpoint_returns_counts(monkeypatch):
    async def fake_get_dashboard_summary(db):
        return {
            'newsTotal': 18,
            'publishedNewsTotal': 9,
            'draftNewsTotal': 5,
            'offlineNewsTotal': 4,
            'categoryTotal': 6,
            'userTotal': 20,
            'adminTotal': 2,
            'recentNewsTotal': 3,
            'recentNews': [{'id': 7, 'title': '最近更新'}],
        }

    monkeypatch.setattr('backend.routers.admin.admin_news.get_dashboard_summary', fake_get_dashboard_summary)

    route_paths = {route.path for route in admin_router.router.routes}
    payload = await admin_router.get_admin_dashboard_summary(
        db=object(),
        admin_user=SimpleNamespace(id=1, role='admin'),
    )
    body = json.loads(payload.body.decode('utf-8'))

    assert '/api/admin/dashboard/summary' in route_paths
    assert body['data']['newsTotal'] == 18
    assert body['data']['recentNews'][0]['title'] == '最近更新'


@pytest.mark.asyncio
async def test_admin_news_list_endpoint_returns_paginated_payload(monkeypatch):
    async def fake_list_news(db, page=1, page_size=10, keyword=None, status=None, category_id=None):
        assert page == 2
        assert page_size == 20
        assert keyword == 'AI'
        assert status == 'published'
        assert category_id == 3
        return {
            'list': [{'id': 8, 'title': '后台新闻'}],
            'total': 21,
            'page': 2,
            'pageSize': 20,
        }

    monkeypatch.setattr('backend.routers.admin.admin_news.list_news', fake_list_news)

    route_paths = {route.path for route in admin_router.router.routes}
    payload = await admin_router.get_admin_news_list(
        db=object(),
        admin_user=SimpleNamespace(id=1, role='admin'),
        page=2,
        page_size=20,
        keyword='AI',
        status='published',
        category_id=3,
    )
    body = json.loads(payload.body.decode('utf-8'))

    assert '/api/admin/news' in route_paths
    assert body['data']['list'][0]['title'] == '后台新闻'
    assert body['data']['total'] == 21
    assert body['data']['page'] == 2
    assert body['data']['pageSize'] == 20


@pytest.mark.asyncio
async def test_admin_news_detail_endpoint_returns_news_item(monkeypatch):
    async def fake_get_news_detail(db, news_id: int):
        assert news_id == 8
        return {'id': 8, 'title': '详情新闻', 'status': 'draft'}

    monkeypatch.setattr('backend.routers.admin.admin_news.get_news_detail', fake_get_news_detail)

    route_paths = {route.path for route in admin_router.router.routes}
    payload = await admin_router.get_admin_news_detail(
        news_id=8,
        db=object(),
        admin_user=SimpleNamespace(id=1, role='admin'),
    )
    body = json.loads(payload.body.decode('utf-8'))

    assert '/api/admin/news/{news_id}' in route_paths
    assert body['data']['title'] == '详情新闻'
    assert body['data']['status'] == 'draft'


@pytest.mark.asyncio
async def test_admin_categories_endpoint_returns_news_count(monkeypatch):
    async def fake_list_categories(db):
        return [{'id': 3, 'name': '科技', 'sortOrder': 1, 'newsCount': 12}]

    monkeypatch.setattr('backend.routers.admin.admin_categories.list_categories', fake_list_categories)

    payload = await admin_router.get_admin_categories(
        db=object(),
        admin_user=SimpleNamespace(id=1, role='admin'),
    )
    body = json.loads(payload.body.decode('utf-8'))

    assert body['data'][0]['newsCount'] == 12
    assert body['data'][0]['sortOrder'] == 1


@pytest.mark.asyncio
async def test_admin_users_endpoint_returns_paginated_list(monkeypatch):
    async def fake_list_users(db, page=1, page_size=10, keyword=None, role=None):
        assert page == 3
        assert page_size == 15
        assert keyword == 'editor'
        assert role == 'admin'
        return {
            'list': [
                {'id': 9, 'username': 'editor', 'nickname': '编辑', 'role': 'admin', 'createdAt': '2026-03-22T10:00:00'}
            ],
            'total': 16,
            'page': 3,
            'pageSize': 15,
        }

    monkeypatch.setattr('backend.routers.admin.admin_users.list_users', fake_list_users)

    payload = await admin_router.get_admin_users(
        db=object(),
        admin_user=SimpleNamespace(id=1, role='admin'),
        page=3,
        page_size=15,
        keyword='editor',
        role='admin',
    )
    body = json.loads(payload.body.decode('utf-8'))

    assert body['data']['list'][0]['username'] == 'editor'
    assert body['data']['total'] == 16
    assert body['data']['pageSize'] == 15


@pytest.mark.asyncio
async def test_admin_update_user_role_endpoint_calls_crud(monkeypatch):
    async def fake_update_user_role(db, user_id: int, role: str):
        assert user_id == 9
        assert role == 'admin'
        return {'id': 9, 'username': 'editor', 'nickname': None, 'role': 'admin', 'createdAt': '2026-03-22T10:00:00'}

    monkeypatch.setattr('backend.routers.admin.admin_users.update_user_role', fake_update_user_role)

    payload = await admin_router.update_admin_user_role(
        user_id=9,
        payload=admin_router.AdminUserRoleUpdateRequest(role='admin'),
        db=object(),
        admin_user=SimpleNamespace(id=1, role='admin'),
    )

    assert '"role":"admin"' in payload.body.decode('utf-8')
