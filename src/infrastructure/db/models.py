from datetime import datetime
import enum
from typing import Annotated
from src.infrastructure.db.base import Base

from sqlalchemy import ForeignKey, String, text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

int_primary_key = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
name_tag = Annotated[str, mapped_column(String(20), nullable=False)]
created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime, mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True)]

class Role(enum.Enum):
    user = "User"
    mod = "Mod"
    admin = "Admin"

class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int_primary_key]
    tag: Mapped[name_tag]
    name: Mapped[name_tag]
    age: Mapped[Annotated[int, mapped_column(nullable=False)]]
    email: Mapped[Annotated[str, mapped_column(unique=True, nullable=False)]]
    password: Mapped[Annotated[str, mapped_column(nullable=False)]]
    role: Mapped[Role]
    created_at: Mapped[created_at]
    city: Mapped[str | None]
    country: Mapped[str | None]
    description: Mapped[Annotated[str, mapped_column(String(500))] | None]

    posts: Mapped[list["PostsOrm"]] = relationship(back_populates="user")
    repr_col = ("id", "tag", "role", "created_at")

class PostsOrm(Base):
    __tablename__ = "posts"

    id: Mapped[int_primary_key]
    user_id: Mapped[Annotated[int, mapped_column(ForeignKey("users.id", ondelete = "CASCADE"))]]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at | None]
    text_content: Mapped[Annotated[str, mapped_column(String(1000), nullable=False)]]

    user: Mapped["UsersOrm"] = relationship(back_populates="posts")
    repr_col = ("id", "user_id", "text_content")