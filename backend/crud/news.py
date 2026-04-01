from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, or_
from backend.models.news import Category
from backend.models.news import News
from backend.models.history import History
from backend.models.favorite import Favorite
from backend.cache import news_cache
from backend.schemas.base import NewsItemBase, build_summary, build_tags

PUBLISHED_STATUS = "published"


def _serialize_news_item(item, hot_score: float | None = None):
    payload = {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "summary": build_summary(item.description, getattr(item, "content", None)),
        "image": item.image,
        "author": item.author,
        "tags": build_tags(item.title, item.author, item.description),
        "categoryId": item.category_id,
        "views": item.views,
        "hotScore": hot_score,
        "publishTime": item.publish_time,
    }
    return NewsItemBase.model_validate(payload)


def _serialize_news_cache_item(item, hot_score: float | None = None):
    payload = _serialize_news_item(item, hot_score=hot_score).model_dump(mode="json", by_alias=False)
    payload["status"] = getattr(item, "status", PUBLISHED_STATUS)
    return payload


def _is_published_cache_item(item: dict) -> bool:
    return item.get("status") == PUBLISHED_STATUS

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
    if news_list is not None and all(_is_published_cache_item(item) for item in news_list):
        return [NewsItemBase.model_validate(item) for item in news_list]

    stmt = (
        select(News)
        .where(News.category_id == category_id, News.status == PUBLISHED_STATUS)
        .order_by(News.views.desc(), News.publish_time.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    news_list_items = [_serialize_news_item(item, hot_score=float(item.views)) for item in news_list]
    news_list_data = [_serialize_news_cache_item(item, hot_score=float(item.views)) for item in news_list]
    await news_cache.set_news_list_cache(category_id, page, limit, news_list_data)
    return news_list_items

async def get_news_count(db: AsyncSession, category_id: int):
    cached_count = await news_cache.get_news_count_cache(category_id)
    if cached_count is not None:
        return cached_count

    stmt = select(func.count(News.id)).where(News.category_id == category_id, News.status == PUBLISHED_STATUS)
    result = await db.execute(stmt)
    count = result.scalar_one()
    await news_cache.set_news_count_cache(category_id, count)
    return count

async def get_news_detail(db: AsyncSession, news_id: int):
    cached_detail = await news_cache.get_news_detail_cache(news_id)
    if cached_detail is not None and cached_detail.get("status") == PUBLISHED_STATUS:
        return News(**cached_detail)

    stmt = select(News).where(News.id == news_id, News.status == PUBLISHED_STATUS)
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
        News.category_id == category_id,
        News.status == PUBLISHED_STATUS,
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    news_recommend_list = result.scalars().all()
    news_recommend_data = [
        {
            **_serialize_news_cache_item(news_detail, hot_score=float(news_detail.views)),
            "content": news_detail.content,
        }
        for news_detail in news_recommend_list
    ]
    await news_cache.set_news_recommend_cache(category_id, news_id, limit, jsonable_encoder(news_recommend_data))
    return news_recommend_data


async def search_news(db: AsyncSession, keyword: str, category_id: int | None = None, skip: int = 0, limit: int = 10):
    pattern = f"%{keyword.strip()}%"
    conditions = [
        or_(
            News.title.ilike(pattern),
            News.description.ilike(pattern),
            News.content.ilike(pattern),
            News.author.ilike(pattern),
        )
    ]
    if category_id is not None:
        conditions.append(News.category_id == category_id)
    conditions.append(News.status == PUBLISHED_STATUS)

    stmt = (
        select(News)
        .where(*conditions)
        .order_by(News.publish_time.desc(), News.views.desc())
        .offset(skip)
        .limit(limit)
    )
    count_stmt = select(func.count(News.id)).where(*conditions)
    result = await db.execute(stmt)
    count_result = await db.execute(count_stmt)
    news_list = result.scalars().all()
    total = count_result.scalar_one()
    return [_serialize_news_item(item, hot_score=float(item.views)) for item in news_list], total


async def get_hot_news(db: AsyncSession, skip: int = 0, limit: int = 10):
    stmt = (
        select(News)
        .where(News.status == PUBLISHED_STATUS)
        .order_by(News.views.desc(), News.publish_time.desc())
        .offset(skip)
        .limit(limit)
    )
    count_stmt = select(func.count(News.id)).where(News.status == PUBLISHED_STATUS)
    result = await db.execute(stmt)
    count_result = await db.execute(count_stmt)
    news_list = result.scalars().all()
    total = count_result.scalar_one()
    return [_serialize_news_item(item, hot_score=float(item.views)) for item in news_list], total


async def get_personalized_news(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    favorite_stmt = (
        select(News.category_id, Favorite.news_id)
        .join(Favorite, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
    )
    history_stmt = (
        select(News.category_id, History.news_id)
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
    )
    favorite_result = await db.execute(favorite_stmt)
    history_result = await db.execute(history_stmt)
    favorite_rows = favorite_result.all()
    history_rows = history_result.all()

    category_scores: dict[int, float] = {}
    excluded_news_ids = {news_id for _, news_id in history_rows}

    for category_id, _ in favorite_rows:
        category_scores[category_id] = category_scores.get(category_id, 0.0) + 3.0
    for category_id, _ in history_rows:
        category_scores[category_id] = category_scores.get(category_id, 0.0) + 1.0

    if not category_scores:
        return await get_hot_news(db, skip=skip, limit=limit)

    candidate_stmt = select(News).where(News.status == PUBLISHED_STATUS)
    if excluded_news_ids:
        candidate_stmt = candidate_stmt.where(News.id.not_in(excluded_news_ids))

    candidate_stmt = candidate_stmt.order_by(News.publish_time.desc(), News.views.desc()).limit(max(limit * 4, 20))
    count_stmt = select(func.count(News.id)).where(News.status == PUBLISHED_STATUS)
    if excluded_news_ids:
        count_stmt = count_stmt.where(News.id.not_in(excluded_news_ids))

    candidate_result = await db.execute(candidate_stmt)
    count_result = await db.execute(count_stmt)
    candidates = candidate_result.scalars().all()
    total = count_result.scalar_one()

    ranked = sorted(
        candidates,
        key=lambda item: (
            category_scores.get(item.category_id, 0.0) * 1000 + item.views,
            item.publish_time,
        ),
        reverse=True,
    )
    paged = ranked[skip: skip + limit]
    return [
        _serialize_news_item(
            item,
            hot_score=category_scores.get(item.category_id, 0.0) * 1000 + float(item.views),
        )
        for item in paged
    ], total
