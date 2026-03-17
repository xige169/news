from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.models.users import User
from backend.schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, \
    UserUpdatePasswordRequest
from backend.config.db_conf import get_db_session
from backend.crud import users
from backend.utils.response import success_response
from backend.utils import auth

router = APIRouter(prefix="/api/user", tags=["user"])

@router.post("/register")
async def register(user_data: UserRequest,db: AsyncSession= Depends(get_db_session)):
    user = await users.get_user_by_username(user_data.username,db)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    new_user =await users.create_user(user_data,db)
    token = await users.create_token(new_user.id,db)
    # return {
    #   "code": 200,
    #   "message": "注册成功",
    #   "data": {
    #     "token": token,
    #     "userInfo": {
    #       "id": new_user.id,
    #       "username": new_user.username,
    #       "bio": new_user.bio,
    #       "avatar": new_user.avatar
    #     }
    #   }
    # }
    response_data = UserAuthResponse(token=token,user_info= UserInfoResponse.model_validate(new_user))
    return success_response(message="注册成功",data=response_data)

@router.post("/login")
async def login(user_data: UserRequest,db: AsyncSession= Depends(get_db_session)):
    user = await users.authenticate_user(user_data.username,user_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = await users.create_token(user.id,db)

    response_data = UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功啦",data=response_data)

@router.get("/info")
async def get_user_info(user: User = Depends(auth.get_current_user)):
    return success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(user))

@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest, user: User = Depends(auth.get_current_user),db: AsyncSession= Depends(get_db_session)):
    user = await users.update_user_info(user_data,user.id,db)
    return success_response(message="更新用户信息成功",data=UserInfoResponse.model_validate(user))

@router.put("/password")
async def update_user_password(user_data: UserUpdatePasswordRequest, user: User = Depends(auth.get_current_user),db: AsyncSession= Depends(get_db_session)):
    update_password = await users.update_password(user_data.old_password,user_data.new_password,user,db)
    if not update_password:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="旧密码错误")
    return success_response(message="密码修改成功")





