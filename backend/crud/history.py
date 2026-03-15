from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.history import History
from backend.models.news import News


async def add_news_history(news_id: int, user_id:int, db: AsyncSession):
    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

async def get_history_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    stmt = select(func.count(History.id)).where(History.user_id == user_id)
    count_result = await db.execute(stmt)
    total = count_result.scalar_one()

    query = (select(News, History.view_time.label("view_time"))
             .join(History, History.news_id == News.id)
             .where(History.user_id == user_id)
             .order_by(History.view_time.desc())
             .offset((page - 1) * page_size)
             .limit(page_size)
             )
    result = await db.execute(query)
    rows = result.all()
    return rows, total

async def delete_one_history(history_id: int, user_id: int, db: AsyncSession):
    stmt = delete(History).where(History.user_id == user_id, History.id == history_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

async def clear_history(user_id: int, db: AsyncSession):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0

