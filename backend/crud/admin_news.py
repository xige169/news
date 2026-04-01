from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.cache import news_cache
from backend.models.news import Category, News
from backend.models.users import User
from backend.schemas.admin import AdminNewsCreateRequest, AdminNewsUpdateRequest
from backend.schemas.base import build_summary


async def _invalidate_news_cache(news: News):
    await news_cache.delete_news_detail_cache(news.id)
    await news_cache.delete_news_list_cache(news.category_id)
    await news_cache.delete_news_count_cache(news.category_id)
    await news_cache.delete_news_recommend_cache_by_category(news.category_id)


def _serialize_news(news: News) -> dict:
    return {
        "id": news.id,
        "title": news.title,
        "description": news.description,
        "summary": build_summary(news.description, news.content),
        "content": news.content,
        "image": news.image,
        "author": news.author,
        "categoryId": news.category_id,
        "views": news.views,
        "status": news.status,
        "isFeatured": news.is_featured,
        "publishTime": news.publish_time,
        "updatedAt": news.updated_at,
    }


async def get_dashboard_summary(db: AsyncSession):
    recent_since = datetime.now() - timedelta(days=7)

    total_result = await db.execute(select(func.count(News.id)))
    published_result = await db.execute(select(func.count(News.id)).where(News.status == "published"))
    draft_result = await db.execute(select(func.count(News.id)).where(News.status == "draft"))
    offline_result = await db.execute(select(func.count(News.id)).where(News.status == "offline"))
    recent_result = await db.execute(select(func.count(News.id)).where(News.created_at >= recent_since))
    category_result = await db.execute(select(func.count(Category.id)))
    user_result = await db.execute(select(func.count(User.id)))
    admin_result = await db.execute(select(func.count(User.id)).where(User.role == "admin"))
    recent_news_result = await db.execute(select(News).order_by(News.updated_at.desc(), News.id.desc()).limit(6))

    return {
        "newsTotal": total_result.scalar_one(),
        "publishedNewsTotal": published_result.scalar_one(),
        "draftNewsTotal": draft_result.scalar_one(),
        "offlineNewsTotal": offline_result.scalar_one(),
        "categoryTotal": category_result.scalar_one(),
        "userTotal": user_result.scalar_one(),
        "adminTotal": admin_result.scalar_one(),
        "recentNewsTotal": recent_result.scalar_one(),
        "recentNews": [_serialize_news(item) for item in recent_news_result.scalars().all()],
    }


async def list_news(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    status: str | None = None,
    category_id: int | None = None,
):
    stmt = select(News)
    count_stmt = select(func.count(News.id))

    if keyword:
        pattern = f"%{keyword.strip()}%"
        condition = or_(
            News.title.ilike(pattern),
            News.description.ilike(pattern),
            News.content.ilike(pattern),
            News.author.ilike(pattern),
        )
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    if status:
        stmt = stmt.where(News.status == status)
        count_stmt = count_stmt.where(News.status == status)

    if category_id is not None:
        stmt = stmt.where(News.category_id == category_id)
        count_stmt = count_stmt.where(News.category_id == category_id)

    offset = max(page - 1, 0) * page_size
    stmt = stmt.order_by(News.updated_at.desc(), News.id.desc()).offset(offset).limit(page_size)

    result = await db.execute(stmt)
    count_result = await db.execute(count_stmt)
    news_list = [_serialize_news(item) for item in result.scalars().all()]

    return {
        "list": news_list,
        "total": count_result.scalar_one(),
        "page": page,
        "pageSize": page_size,
    }


async def get_news_detail(db: AsyncSession, news_id: int):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if news is None:
        raise HTTPException(status_code=404, detail="新闻不存在")
    return _serialize_news(news)


async def create_news(db: AsyncSession, payload: AdminNewsCreateRequest):
    news = News(**payload.model_dump(by_alias=False, exclude_none=True))
    if news.publish_time is None:
        news.publish_time = datetime.now()
    db.add(news)
    await db.commit()
    await db.refresh(news)
    await _invalidate_news_cache(news)
    return _serialize_news(news)


async def update_news(db: AsyncSession, news_id: int, payload: AdminNewsUpdateRequest):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if news is None:
        raise HTTPException(status_code=404, detail="新闻不存在")

    old_category_id = news.category_id
    for field, value in payload.model_dump(by_alias=False, exclude_none=True).items():
        setattr(news, field, value)
    db.add(news)
    await db.commit()
    await db.refresh(news)
    await _invalidate_news_cache(news)
    if old_category_id != news.category_id:
        await news_cache.delete_news_list_cache(old_category_id)
        await news_cache.delete_news_count_cache(old_category_id)
        await news_cache.delete_news_recommend_cache_by_category(old_category_id)
    return _serialize_news(news)


async def update_news_status(db: AsyncSession, news_id: int, status: str):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if news is None:
        raise HTTPException(status_code=404, detail="新闻不存在")

    news.status = status
    db.add(news)
    await db.commit()
    await db.refresh(news)
    await _invalidate_news_cache(news)
    return _serialize_news(news)


async def delete_news(db: AsyncSession, news_id: int):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if news is None:
        raise HTTPException(status_code=404, detail="新闻不存在")

    category_id = news.category_id
    await db.delete(news)
    await db.commit()
    await news_cache.delete_news_detail_cache(news_id)
    await news_cache.delete_news_list_cache(category_id)
    await news_cache.delete_news_count_cache(category_id)
    await news_cache.delete_news_recommend_cache_by_category(category_id)
    return True
