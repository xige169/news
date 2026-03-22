from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.cache import news_cache
from backend.config import cache_conf
from backend.models.news import Category, News
from backend.schemas.admin import AdminCategoryRequest


async def list_categories(db: AsyncSession):
    stmt = (
        select(
            Category.id,
            Category.name,
            Category.sort_order,
            func.count(News.id).label("news_count"),
        )
        .outerjoin(News, News.category_id == Category.id)
        .group_by(Category.id, Category.name, Category.sort_order)
        .order_by(Category.sort_order.asc(), Category.id.asc())
    )
    result = await db.execute(stmt)

    return [
        {
            "id": row.id,
            "name": row.name,
            "sortOrder": row.sort_order,
            "newsCount": row.news_count,
        }
        for row in result.all()
    ]


async def create_category(db: AsyncSession, payload: AdminCategoryRequest):
    category = Category(**payload.model_dump(by_alias=False))
    db.add(category)
    await db.commit()
    await db.refresh(category)
    await cache_conf.delete_cache(news_cache.CATEGORIES_kEY)
    return {
        "id": category.id,
        "name": category.name,
        "sortOrder": category.sort_order,
        "newsCount": 0,
    }


async def update_category(db: AsyncSession, category_id: int, payload: AdminCategoryRequest):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="分类不存在")

    for field, value in payload.model_dump(by_alias=False).items():
        setattr(category, field, value)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    await cache_conf.delete_cache(news_cache.CATEGORIES_kEY)
    await news_cache.delete_news_list_cache(category.id)
    await news_cache.delete_news_recommend_cache_by_category(category.id)
    return {
        "id": category.id,
        "name": category.name,
        "sortOrder": category.sort_order,
        "newsCount": 0,
    }


async def delete_category(db: AsyncSession, category_id: int):
    count_result = await db.execute(select(func.count(News.id)).where(News.category_id == category_id))
    if count_result.scalar_one() > 0:
        raise HTTPException(status_code=400, detail="分类下仍有新闻，不能删除")

    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="分类不存在")

    await db.delete(category)
    await db.commit()
    await cache_conf.delete_cache(news_cache.CATEGORIES_kEY)
    return True
