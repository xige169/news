from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import and_, delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.comment import Comment, CommentLike
from backend.models.news import News
from backend.models.users import User


DELETED_PLACEHOLDER = ""


async def _news_exists(db: AsyncSession, news_id: int) -> bool:
    result = await db.execute(select(News.id).where(News.id == news_id))
    return result.scalar_one_or_none() is not None


async def add_comment(
    db: AsyncSession,
    user_id: int,
    news_id: int,
    content: str,
    parent_id: Optional[int],
) -> Comment:
    if not await _news_exists(db, news_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="新闻不存在")

    root_id: Optional[int] = None
    if parent_id is not None:
        result = await db.execute(
            select(Comment).where(
                Comment.id == parent_id,
                Comment.news_id == news_id,
                Comment.is_deleted.is_(False),
            )
        )
        parent = result.scalar_one_or_none()
        if parent is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="父评论不存在或已删除")
        root_id = parent.root_id or parent.id

    comment = Comment(
        news_id=news_id,
        user_id=user_id,
        parent_id=parent_id,
        root_id=root_id,
        content=content,
        like_count=0,
        is_deleted=False,
    )
    db.add(comment)
    await db.flush()
    if comment.root_id is None:
        comment.root_id = comment.id
    await db.commit()
    await db.refresh(comment)
    return comment


async def list_top_level_ids(
    db: AsyncSession,
    news_id: int,
    page: int,
    page_size: int,
) -> Tuple[List[int], int]:
    count_stmt = select(func.count(Comment.id)).where(
        Comment.news_id == news_id,
        Comment.parent_id.is_(None),
    )
    total = (await db.execute(count_stmt)).scalar_one()

    list_stmt = (
        select(Comment.id)
        .where(Comment.news_id == news_id, Comment.parent_id.is_(None))
        .order_by(Comment.created_at.desc(), Comment.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(list_stmt)
    ids = [row[0] for row in result.all()]
    return ids, total


async def fetch_thread_rows(
    db: AsyncSession,
    root_ids: List[int],
    current_user_id: Optional[int],
):
    """
    返回 (Comment, user_name, user_avatar, liked_bool) 行集合，覆盖给定 root_ids 的整棵树。
    """
    if not root_ids:
        return []

    base_stmt = (
        select(
            Comment,
            User.nickname,
            User.username,
            User.avatar,
        )
        .join(User, User.id == Comment.user_id)
        .where(Comment.root_id.in_(root_ids))
        .order_by(Comment.created_at.asc(), Comment.id.asc())
    )
    rows = (await db.execute(base_stmt)).all()
    if not rows:
        return []

    liked_ids: set[int] = set()
    if current_user_id is not None:
        comment_ids = [r[0].id for r in rows]
        like_stmt = select(CommentLike.comment_id).where(
            CommentLike.user_id == current_user_id,
            CommentLike.comment_id.in_(comment_ids),
        )
        liked_ids = {row[0] for row in (await db.execute(like_stmt)).all()}

    enriched = []
    for comment, nickname, username, avatar in rows:
        display_name = nickname or username
        enriched.append((comment, display_name, avatar, comment.id in liked_ids))
    return enriched


def build_tree(top_level_ids: List[int], rows) -> List[dict]:
    """
    把扁平行集合按 parent_id 组装为有序树。返回 dict 列表，含 replies 子树。
    顶层结果按 top_level_ids 顺序输出（即与分页排序一致）。
    """
    nodes: dict[int, dict] = {}
    for comment, user_name, user_avatar, liked in rows:
        nodes[comment.id] = {
            "id": comment.id,
            "newsId": comment.news_id,
            "userId": None if comment.is_deleted else comment.user_id,
            "userName": None if comment.is_deleted else user_name,
            "userAvatar": None if comment.is_deleted else user_avatar,
            "parentId": comment.parent_id,
            "content": DELETED_PLACEHOLDER if comment.is_deleted else comment.content,
            "likeCount": comment.like_count,
            "liked": liked,
            "isDeleted": comment.is_deleted,
            "createdAt": comment.created_at.isoformat() if comment.created_at else None,
            "replies": [],
        }

    for node in nodes.values():
        parent_id = node["parentId"]
        if parent_id is not None and parent_id in nodes:
            nodes[parent_id]["replies"].append(node)

    return [nodes[i] for i in top_level_ids if i in nodes]


async def delete_own_comment(db: AsyncSession, user_id: int, comment_id: int) -> str:
    """
    返回 'ok' / 'not_found' / 'forbidden' / 'already_deleted'
    """
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment is None:
        return "not_found"
    if comment.user_id != user_id:
        return "forbidden"
    if comment.is_deleted:
        return "already_deleted"
    comment.is_deleted = True
    comment.content = DELETED_PLACEHOLDER
    await db.commit()
    return "ok"


async def toggle_like(
    db: AsyncSession,
    user_id: int,
    comment_id: int,
    like: bool,
) -> Tuple[int, bool]:
    """
    幂等：like=True 时若已点赞则不重复加；like=False 时若未点赞则不报错。
    返回 (like_count_after, liked_after)。
    """
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment is None or comment.is_deleted:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="评论不存在或已删除")

    existing = await db.execute(
        select(CommentLike.id).where(
            CommentLike.user_id == user_id,
            CommentLike.comment_id == comment_id,
        )
    )
    existing_id = existing.scalar_one_or_none()

    if like and existing_id is None:
        await db.execute(
            insert(CommentLike).values(user_id=user_id, comment_id=comment_id)
        )
        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(like_count=Comment.like_count + 1)
        )
    elif not like and existing_id is not None:
        await db.execute(
            delete(CommentLike).where(CommentLike.id == existing_id)
        )
        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id, Comment.like_count > 0)
            .values(like_count=Comment.like_count - 1)
        )
    await db.commit()

    refreshed = await db.execute(
        select(Comment.like_count).where(Comment.id == comment_id)
    )
    final_count = refreshed.scalar_one()
    return final_count, like
