from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.config.db_conf import get_db_session
from backend.crud import users


async def get_current_user(authorization: str=Header(..., alias="Authorization"),db: AsyncSession= Depends(get_db_session)):
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌或者令牌已过期")

    token = parts[1]
    user = await users.get_user_by_token(token,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌或者令牌已过期")
    return  user
