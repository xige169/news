from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from backend.models.news import Category
from backend.models.news import News
from backend.cache import news_cache
from backend.schemas.base import NewsItemBase

async def get_categories(db: AsyncSession ,skip: int = 0, limit: int = 100):
    categories = await news_cache.get_categories_cache()
    if categories is not None:
        return categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()
    categories_data = jsonable_encoder(categories)
    await news_cache.set_categories_cache(categories_data)
    return categories_data

async def get_news_list(db: AsyncSession, category_id: int, skip: int= 0, limit: int =10):
    page =(skip//limit) + 1
    news_list = await news_cache.get_news_list_cache(category_id, page, limit)
    if news_list is not None:
        return [NewsItemBase.model_validate(item) for item in news_list]

    stmt = select(News).where(News.category_id == category_id).order_by(News.views.desc(), News.publish_time.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    news_list_items = [NewsItemBase.model_validate(item) for item in news_list]
    news_list_data = [item.model_dump(mode="json", by_alias=False) for item in news_list_items]
    await news_cache.set_news_list_cache(category_id, page, limit, news_list_data)
    return news_list_items

async def get_news_count(db: AsyncSession, category_id: int):
    cached_count = await news_cache.get_news_count_cache(category_id)
    if cached_count is not None:
        return cached_count

    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    count = result.scalar_one()
    await news_cache.set_news_count_cache(category_id, count)
    return count

async def get_news_detail(db: AsyncSession, news_id: int):
    cached_detail = await news_cache.get_news_detail_cache(news_id)
    if cached_detail is not None:
        return News(**cached_detail)

    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news_detail = result.scalar_one_or_none()
    if news_detail is not None:
        await news_cache.set_news_detail_cache(news_id, jsonable_encoder(news_detail))
    return news_detail

async def update_news_views(db: AsyncSession, news_id: int):
    category_stmt = select(News.category_id).where(News.id == news_id)
    category_result = await db.execute(category_stmt)
    category_id = category_result.scalar_one_or_none()
    if category_id is None:
        return False

    stmt = update(News).where(News.id == news_id).values(views = News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount > 0:
        await news_cache.delete_news_detail_cache(news_id)
        await news_cache.delete_news_list_cache(category_id)
        await news_cache.delete_news_recommend_cache_by_category(category_id)

    return result.rowcount > 0

async def get_news_recommend(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    cached_recommend = await news_cache.get_news_recommend_cache(category_id, news_id, limit)
    if cached_recommend is not None:
        return cached_recommend

    stmt = select(News).where(
        News.id != news_id,
        News.category_id == category_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    news_recommend_list = result.scalars().all()
    news_recommend_data = [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views
    } for news_detail in news_recommend_list]
    await news_cache.set_news_recommend_cache(category_id, news_id, limit, jsonable_encoder(news_recommend_data))
    return news_recommend_data
