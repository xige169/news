from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.favorite import Favorite
from backend.models.news import News


async def is_news_favorite(news_id: int, user_id: int, db: AsyncSession):
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None

async def add_news_favorite(news_id: int, user_id: int, db: AsyncSession):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def remove_news_favorite(news_id: int, user_id: int, db: AsyncSession):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

async def get_favorite_list(db:AsyncSession, page: int = 1, page_size: int = 10, user_id: int = 1):
    stmt = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    count_result = await db.execute(stmt)
    total = count_result.scalar_one()

    query = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
             .join(Favorite, Favorite.news_id == News.id)
             .where(Favorite.user_id == user_id)
              .order_by(Favorite.created_at.desc())
             .offset((page - 1) * page_size)
             .limit(page_size)
             )

    result = await db.execute(query)
    rows = result.all()
    return rows, total

async def clear_favorite_list(db: AsyncSession, user_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0




