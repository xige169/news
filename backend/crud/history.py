from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.history import History
from backend.models.news import News


async def add_news_history(news_id: int, user_id:int, db: AsyncSession):
    stmt = (
        select(History)
        .where(History.user_id == user_id, History.news_id == news_id)
        .order_by(History.view_time.desc(), History.id.desc())
    )
    result = await db.execute(stmt)
    if hasattr(result, "scalars"):
        histories = result.scalars().all()
    else:
        history = result.scalar_one_or_none()
        histories = [history] if history is not None else []

    if histories:
        history = histories[0]
        history.view_time = datetime.now()
        duplicate_ids = [item.id for item in histories[1:]]
        if duplicate_ids:
            await db.execute(delete(History).where(History.id.in_(duplicate_ids)))
        await db.commit()
        return history

    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

async def get_history_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    latest_history = (
        select(
            History.id.label("history_id"),
            History.news_id.label("news_id"),
            History.view_time.label("view_time"),
            func.row_number().over(
                partition_by=History.news_id,
                order_by=(History.view_time.desc(), History.id.desc())
            ).label("row_num")
        )
        .where(History.user_id == user_id)
        .subquery()
    )

    latest_history_rows = (
        select(
            latest_history.c.history_id,
            latest_history.c.news_id,
            latest_history.c.view_time
        )
        .where(latest_history.c.row_num == 1)
        .subquery()
    )

    stmt = select(func.count()).select_from(latest_history_rows)
    count_result = await db.execute(stmt)
    total = count_result.scalar_one()

    query = (select(News, latest_history_rows.c.view_time, latest_history_rows.c.history_id)
             .join(latest_history_rows, latest_history_rows.c.news_id == News.id)
             .order_by(latest_history_rows.c.view_time.desc())
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
