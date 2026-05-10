from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.news import News
from backend.models.users import Base, User


class Comment(Base):
    """
    评论表ORM模型
    """

    __tablename__ = "comment"
    __table_args__ = (
        Index("idx_news_root_created", "news_id", "root_id", "created_at"),
        Index("fk_comment_user_idx", "user_id"),
        Index("fk_comment_parent_idx", "parent_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="评论ID"
    )
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(News.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="新闻ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(User.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="评论者ID"
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("comment.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
        comment="父评论ID，NULL 表示一级评论"
    )
    root_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="所属一级评论ID，自身为根时等于自身ID"
    )
    content: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        default="",
        comment="评论正文"
    )
    like_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="点赞数（反规范化）"
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否已删除（软删）"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="创建时间"
    )

    def __repr__(self):
        return f"<Comment(id={self.id}, news_id={self.news_id}, user_id={self.user_id}, parent_id={self.parent_id})>"


class CommentLike(Base):
    """
    评论点赞表ORM模型
    """

    __tablename__ = "comment_like"
    __table_args__ = (
        Index("uniq_user_comment", "user_id", "comment_id", unique=True),
        Index("fk_comment_like_comment_idx", "comment_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="点赞ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(User.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    comment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(Comment.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="评论ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="点赞时间"
    )

    def __repr__(self):
        return f"<CommentLike(id={self.id}, user_id={self.user_id}, comment_id={self.comment_id})>"
