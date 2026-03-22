from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.config.db_conf import get_db_session
from backend.config import cache_conf
from backend.crud import users
from backend.models.users import User
from backend.utils.jwt import decode_access_token, get_token_ttl


BLACKLIST_PREFIX = "auth:blacklist:"


async def is_token_blacklisted(token: str) -> bool:
    cached = await cache_conf.get_cache(f"{BLACKLIST_PREFIX}{token}")
    return cached is not None


async def blacklist_token(token: str) -> bool:
    ttl = get_token_ttl(token)
    if ttl <= 0:
        return True
    return await cache_conf.set_cache(f"{BLACKLIST_PREFIX}{token}", True, ttl)


async def get_current_user(authorization: str=Header(..., alias="Authorization"),db: AsyncSession= Depends(get_db_session)):
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌或者令牌已过期")

    token = parts[1]
    try:
        payload = decode_access_token(token)
        if payload.get("type") != "access":
            raise ValueError("invalid token type")
        if await is_token_blacklisted(token):
            raise ValueError("token blacklisted")
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌或者令牌已过期")

    user = await users.get_user_by_id(user_id,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌或者令牌已过期")
    return  user


async def require_admin_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    user = await get_current_user(authorization=authorization, db=db)
    if getattr(user, "role", "user") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有管理员权限")
    return user
