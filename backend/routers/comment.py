from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.db_conf import get_db_session
from backend.crud import comment as comment_crud
from backend.models.users import User
from backend.schemas.comment import (
    CommentCreateRequest,
    CommentLikeRequest,
)
from backend.utils import auth
from backend.utils.response import success_response


router = APIRouter(prefix="/api/comment", tags=["comment"])


@router.post("/add")
async def add_comment(
    payload: CommentCreateRequest,
    user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    comment = await comment_crud.add_comment(
        db,
        user_id=user.id,
        news_id=payload.news_id,
        content=payload.content,
        parent_id=payload.parent_id,
    )
    data = {
        "id": comment.id,
        "newsId": comment.news_id,
        "userId": comment.user_id,
        "userName": user.nickname or user.username,
        "userAvatar": user.avatar,
        "parentId": comment.parent_id,
        "content": comment.content,
        "likeCount": comment.like_count,
        "liked": False,
        "isDeleted": comment.is_deleted,
        "createdAt": comment.created_at.isoformat() if comment.created_at else None,
        "replies": [],
    }
    return success_response(message="评论发表成功", data=data)


@router.get("/list")
async def list_comments(
    news_id: int = Query(..., alias="newsId"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, le=100, alias="pageSize"),
    current_user: Optional[User] = Depends(auth.get_optional_user),
    db: AsyncSession = Depends(get_db_session),
):
    top_ids, total = await comment_crud.list_top_level_ids(db, news_id, page, page_size)
    rows = await comment_crud.fetch_thread_rows(
        db, top_ids, current_user.id if current_user else None
    )
    tree = comment_crud.build_tree(top_ids, rows)
    has_more = total > page * page_size
    return success_response(
        message="获取评论列表成功",
        data={"list": tree, "total": total, "hasMore": has_more},
    )


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    result = await comment_crud.delete_own_comment(db, user.id, comment_id)
    if result == "not_found":
        raise HTTPException(status_code=404, detail="评论不存在")
    if result == "forbidden":
        raise HTTPException(status_code=403, detail="只能删除自己的评论")
    if result == "already_deleted":
        raise HTTPException(status_code=400, detail="评论已删除")
    return success_response(message="删除评论成功")


@router.post("/{comment_id}/like")
async def like_comment(
    comment_id: int,
    payload: CommentLikeRequest,
    user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    like_count, liked = await comment_crud.toggle_like(
        db, user.id, comment_id, payload.like
    )
    return success_response(
        message="操作成功",
        data={"commentId": comment_id, "likeCount": like_count, "liked": liked},
    )
