from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud import users


async def list_users(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    role: str | None = None,
):
    return await users.list_users(db, page=page, page_size=page_size, keyword=keyword, role=role)


async def update_user_role(db: AsyncSession, user_id: int, role: str):
    return await users.update_user_role(db, user_id, role)
