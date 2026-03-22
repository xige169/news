from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.db_conf import get_db_session
from backend.crud import admin_categories, admin_news, admin_users
from backend.models.users import User
from backend.schemas.admin import (
    AdminCategoryRequest,
    AdminNewsCreateRequest,
    AdminNewsStatusUpdateRequest,
    AdminNewsUpdateRequest,
    AdminUserRoleUpdateRequest,
)
from backend.utils import auth
from backend.utils.response import success_response

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard/summary")
async def get_admin_dashboard_summary(
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    summary = await admin_news.get_dashboard_summary(db)
    return success_response(message="获取后台总览成功", data=summary)


@router.get("/news")
async def get_admin_news_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, alias="pageSize", ge=1, le=100),
    keyword: str | None = Query(default=None),
    status: str | None = Query(default=None),
    category_id: int | None = Query(default=None, alias="categoryId"),
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    news_list = await admin_news.list_news(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
        category_id=category_id,
    )
    return success_response(message="获取后台新闻列表成功", data=news_list)


@router.get("/news/{news_id}")
async def get_admin_news_detail(
    news_id: int,
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    news_item = await admin_news.get_news_detail(db, news_id)
    return success_response(message="获取新闻详情成功", data=news_item)


@router.post("/news")
async def create_admin_news(
    payload: AdminNewsCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    news_item = await admin_news.create_news(db, payload)
    return success_response(message="创建新闻成功", data=news_item)


@router.put("/news/{news_id}")
async def update_admin_news(
    news_id: int,
    payload: AdminNewsUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    news_item = await admin_news.update_news(db, news_id, payload)
    return success_response(message="更新新闻成功", data=news_item)


@router.put("/news/{news_id}/status")
async def update_admin_news_status(
    news_id: int,
    payload: AdminNewsStatusUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    news_item = await admin_news.update_news_status(db, news_id, payload.status)
    return success_response(message="更新新闻状态成功", data=news_item)


@router.delete("/news/{news_id}")
async def delete_admin_news(
    news_id: int,
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    await admin_news.delete_news(db, news_id)
    return success_response(message="删除新闻成功")


@router.get("/categories")
async def get_admin_categories(
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    categories = await admin_categories.list_categories(db)
    return success_response(message="获取分类成功", data=categories)


@router.post("/categories")
async def create_admin_category(
    payload: AdminCategoryRequest,
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    category = await admin_categories.create_category(db, payload)
    return success_response(message="创建分类成功", data=category)


@router.put("/categories/{category_id}")
async def update_admin_category(
    category_id: int,
    payload: AdminCategoryRequest,
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    category = await admin_categories.update_category(db, category_id, payload)
    return success_response(message="更新分类成功", data=category)


@router.delete("/categories/{category_id}")
async def delete_admin_category(
    category_id: int,
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    await admin_categories.delete_category(db, category_id)
    return success_response(message="删除分类成功")


@router.get("/users")
async def get_admin_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, alias="pageSize", ge=1, le=100),
    keyword: str | None = Query(default=None),
    role: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    user_list = await admin_users.list_users(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        role=role,
    )

    if isinstance(user_list, dict) and "list" in user_list:
        user_list["list"] = [
            {
                "id": item.id,
                "username": item.username,
                "nickname": item.nickname,
                "role": item.role,
                "createdAt": item.created_at,
            }
            if not isinstance(item, dict)
            else item
            for item in user_list["list"]
        ]
    return success_response(message="获取用户成功", data=user_list)


@router.put("/users/{user_id}/role")
async def update_admin_user_role(
    user_id: int,
    payload: AdminUserRoleUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    admin_user: User = Depends(auth.require_admin_user),
):
    user = await admin_users.update_user_role(db, user_id=user_id, role=payload.role)
    data = user
    if not isinstance(user, dict):
        data = {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "role": user.role,
            "createdAt": user.created_at,
        }
    return success_response(message="更新用户角色成功", data=data)
