from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.comment import Comment
from backend.models.news import News
from backend.models.users import User


async def admin_list_comments(
    db: AsyncSession,
    *,
    keyword: Optional[str] = None,
    news_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[list[dict], int]:
    filters = []
    if news_id is not None:
        filters.append(Comment.news_id == news_id)
    if keyword:
        like = f"%{keyword}%"
        filters.append(or_(Comment.content.like(like), User.username.like(like), News.title.like(like)))

    base = (
        select(Comment, News.title, User.username, User.nickname)
        .join(News, News.id == Comment.news_id)
        .join(User, User.id == Comment.user_id)
    )
    if filters:
        base = base.where(*filters)

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    list_stmt = (
        base.order_by(Comment.created_at.desc(), Comment.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await db.execute(list_stmt)).all()

    items = []
    for comment, news_title, username, nickname in rows:
        items.append(
            {
                "id": comment.id,
                "newsId": comment.news_id,
                "newsTitle": news_title,
                "userId": comment.user_id,
                "userName": nickname or username,
                "parentId": comment.parent_id,
                "content": comment.content,
                "likeCount": comment.like_count,
                "isDeleted": comment.is_deleted,
                "createdAt": comment.created_at.isoformat() if comment.created_at else None,
            }
        )
    return items, total


async def admin_delete_comment(db: AsyncSession, comment_id: int) -> str:
    """返回 'ok' / 'not_found' / 'already_deleted'"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment is None:
        return "not_found"
    if comment.is_deleted:
        return "already_deleted"
    comment.is_deleted = True
    comment.content = ""
    await db.commit()
    return "ok"
