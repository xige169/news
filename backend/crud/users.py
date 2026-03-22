from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.schemas.users import UserRequest, UserUpdateRequest
from backend.models.users import User
from backend.utils import security
from backend.utils.jwt import create_access_token, create_refresh_token, decode_access_token
from sqlalchemy import func, or_, select, update

async def get_user_by_username(username: str, db: AsyncSession):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_id(user_id: int, db: AsyncSession):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(user_data: UserRequest, db: AsyncSession):
    hashed_pwd = security.get_hash_pwd(user_data.password)
    user = User(username=user_data.username, password=hashed_pwd)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_token(user_id: int, db: AsyncSession | None = None):
    return create_access_token(user_id)


async def create_auth_tokens(user_id: int):
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    return {
        "token": access_token,
        "accessToken": access_token,
        "refreshToken": refresh_token,
    }

async def authenticate_user(username: str, password: str, db: AsyncSession):
    user = await get_user_by_username(username, db)
    if not user:
        return None
    if not security.verify_pwd(password, user.password):
        return None
    return user

async def get_user_by_token(token: str, db: AsyncSession):
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        return None
    return await get_user_by_id(user_id, db)


async def refresh_auth_tokens(refresh_token: str, db: AsyncSession):
    try:
        payload = decode_access_token(refresh_token)
        if payload.get("type") != "refresh":
            return None
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        return None

    user = await get_user_by_id(user_id, db)
    if not user:
        return None

    return await create_auth_tokens(user_id)

async def update_user_info(user_data: UserUpdateRequest, user_id: int, db: AsyncSession):
    query = update(User).where(User.id == user_id).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none= True
    ))
    result = await db.execute(query)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")

    return await get_user_by_id(user_id, db)

async def update_password(old_password: str, new_password: str, user: User,db: AsyncSession):
    if not security.verify_pwd(old_password, user.password):
        return False

    user.password = security.get_hash_pwd(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True


async def list_users(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    role: str | None = None,
):
    stmt = select(User)
    count_stmt = select(func.count(User.id))

    if keyword:
        pattern = f"%{keyword.strip()}%"
        condition = or_(
            User.username.ilike(pattern),
            User.nickname.ilike(pattern),
            User.phone.ilike(pattern),
        )
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    if role:
        stmt = stmt.where(User.role == role)
        count_stmt = count_stmt.where(User.role == role)

    offset = max(page - 1, 0) * page_size
    stmt = stmt.order_by(User.created_at.desc(), User.id.desc()).offset(offset).limit(page_size)

    result = await db.execute(stmt)
    count_result = await db.execute(count_stmt)
    user_list = result.scalars().all()
    total = count_result.scalar_one()

    return {
        "list": user_list,
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


async def update_user_role(db: AsyncSession, user_id: int, role: str):
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.role = role
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
