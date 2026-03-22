from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    用户信息表ORM模型
    """

    __tablename__ = "user"
    __table_args__ = (
        Index("username_UNIQUE", "username", unique=True),
        Index("phone_UNIQUE", "phone", unique=True),
    )

    tokens: Mapped[list["UserToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="用户ID"
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="用户名"
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码（加密存储）"
    )
    nickname: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="昵称"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        default="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg",
        comment="头像URL"
    )
    gender: Mapped[Optional[str]] = mapped_column(
        Enum("male", "female", "unknown", name="user_gender_enum"),
        nullable=True,
        default="unknown",
        comment="性别"
    )
    bio: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        default="这个人很懒，什么也没留下",
        comment="个人简介"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
        comment="手机号"
    )
    role: Mapped[str] = mapped_column(
        Enum("user", "admin", name="user_role_enum"),
        nullable=False,
        default="user",
        comment="用户角色"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
        comment="更新时间"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class UserToken(Base):
    """
    用户令牌表ORM模型
    """

    __tablename__ = "user_token"
    __table_args__ = (
        Index("token_UNIQUE", "token", unique=True),
        Index("fk_user_token_user_idx", "user_id"),
    )

    user: Mapped["User"] = relationship(back_populates="tokens")

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="令牌ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    token: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="令牌值"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="过期时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="创建时间"
    )

    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id}, token={self.token})>"
