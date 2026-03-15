from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str =Field(...)
    password: str = Field(...)

class UserInfoBase(BaseModel):
    nickname:Optional[str] = Field(None,max_length=50,description="昵称")
    avatar:Optional[str] = Field(None,max_length=255,description="头像URL")
    gender:Optional[str] = Field(None,max_length=10,description="性别")
    bio:Optional[str] = Field(None,max_length=500,description="个人简介")

class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse= Field(..., alias="userInfo")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes= True
    )

class UserUpdateRequest(BaseModel):
    nickname:Optional[str] = Field(None,max_length=50,description="昵称")
    avatar:Optional[str] = Field(None,max_length=255,description="头像URL")
    gender:Optional[str] = Field(None,max_length=10,description="性别")
    bio:Optional[str] = Field(None,max_length=500,description="个人简介")
    phone:Optional[str] = Field(None,max_length=20,description="手机号")

class UserUpdatePasswordRequest(BaseModel):
    old_password: str = Field(...,max_length=255,alias="oldPassword",description="旧密码")
    new_password: str = Field(...,max_length=255,alias="newPassword",description="新密码")