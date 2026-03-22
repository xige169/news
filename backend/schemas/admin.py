from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.users import UserRole

NewsStatus = Literal["draft", "published", "offline"]


class AdminNewsCreateRequest(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    content: str = Field(...)
    image: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=50)
    category_id: int = Field(..., alias="categoryId")
    status: NewsStatus = Field(default="draft")
    is_featured: bool = Field(default=False, alias="isFeatured")
    publish_time: Optional[datetime] = Field(None, alias="publishTime")

    model_config = ConfigDict(populate_by_name=True)


class AdminNewsUpdateRequest(AdminNewsCreateRequest):
    pass


class AdminNewsStatusUpdateRequest(BaseModel):
    status: NewsStatus


class AdminCategoryRequest(BaseModel):
    name: str = Field(..., max_length=50)
    sort_order: int = Field(default=0, alias="sortOrder")

    model_config = ConfigDict(populate_by_name=True)


class AdminUserRoleUpdateRequest(BaseModel):
    role: UserRole


class AdminCategoryResponse(BaseModel):
    id: int
    name: str
    sort_order: int = Field(alias="sortOrder")
    news_count: int = Field(default=0, alias="newsCount")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminUserResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    role: UserRole
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
