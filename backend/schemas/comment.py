from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CommentCreateRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")
    content: str = Field(..., min_length=1, max_length=1000)
    parent_id: Optional[int] = Field(default=None, alias="parentId")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("content")
    @classmethod
    def _strip_content(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("评论内容不能为空")
        return stripped


class CommentLikeRequest(BaseModel):
    like: bool = Field(...)


class CommentResponse(BaseModel):
    id: int
    news_id: int = Field(..., alias="newsId")
    user_id: Optional[int] = Field(None, alias="userId")
    user_name: Optional[str] = Field(None, alias="userName")
    user_avatar: Optional[str] = Field(None, alias="userAvatar")
    parent_id: Optional[int] = Field(None, alias="parentId")
    content: str
    like_count: int = Field(..., alias="likeCount")
    liked: bool = False
    is_deleted: bool = Field(..., alias="isDeleted")
    created_at: datetime = Field(..., alias="createdAt")
    replies: List["CommentResponse"] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


CommentResponse.model_rebuild()


class CommentListResponse(BaseModel):
    list: List[CommentResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(populate_by_name=True)


class CommentLikeResultResponse(BaseModel):
    comment_id: int = Field(..., alias="commentId")
    like_count: int = Field(..., alias="likeCount")
    liked: bool

    model_config = ConfigDict(populate_by_name=True)


class AdminCommentItemResponse(BaseModel):
    id: int
    news_id: int = Field(..., alias="newsId")
    news_title: Optional[str] = Field(None, alias="newsTitle")
    user_id: int = Field(..., alias="userId")
    user_name: Optional[str] = Field(None, alias="userName")
    parent_id: Optional[int] = Field(None, alias="parentId")
    content: str
    like_count: int = Field(..., alias="likeCount")
    is_deleted: bool = Field(..., alias="isDeleted")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)


class AdminCommentListResponse(BaseModel):
    list: List[AdminCommentItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(populate_by_name=True)
