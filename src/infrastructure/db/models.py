import enum
from typing import Annotated
from src.infrastructure.db.base import Base, int_primary_key, created_at, updated_at
from src.infrastructure.db.media import PFPsOrm, AttachedMediasOrm

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Role(enum.Enum):
    user = "User"
    mod = "Mod"
    admin = "Admin"

class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[int_primary_key]
    tag: Mapped[Annotated[str, mapped_column(String(20), unique=True, nullable=False)]]
    name: Mapped[Annotated[str, mapped_column(String(20), nullable=False)]]
    age: Mapped[Annotated[int, mapped_column(nullable=False)]]
    email: Mapped[Annotated[str, mapped_column(unique=True, nullable=False)]]
    password: Mapped[Annotated[str, mapped_column(nullable=False)]]
    is_active: Mapped[Annotated[bool, mapped_column(default=True, server_default=text("true"))]]
    role: Mapped[Role]
    created_at: Mapped[created_at]
    city: Mapped[str | None]
    country: Mapped[str | None]
    description: Mapped[Annotated[str, mapped_column(String(500))] | None]

    posts: Mapped[list["PostsOrm"]] = relationship(back_populates="user", passive_deletes=True)
    pfp: Mapped["PFPsOrm | None"] = relationship(
        back_populates="user",
        passive_deletes=True,
        cascade="all, delete-orphan",
        single_parent=True,
    )
    repr_col = ("id", "tag", "role", "created_at")

    @property
    def pfp_url(self) -> str | None:
        return self.pfp.url if self.pfp else None

class PostsOrm(Base):
    __tablename__ = "posts"

    id: Mapped[int_primary_key]
    user_id: Mapped[Annotated[int, mapped_column(ForeignKey("users.id", ondelete = "CASCADE"))]]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at | None]
    text_content: Mapped[Annotated[str, mapped_column(String(1000), nullable=False)]]

    user: Mapped["UsersOrm"] = relationship(back_populates="posts")
    attached_medias: Mapped[list["AttachedMediasOrm"] | None] = relationship(
        back_populates="post",
        passive_deletes=True,
    )
    repr_col = ("id", "user_id", "text_content")

    @property
    def media_urls(self) -> list[str]:
        if not self.attached_medias:
            return []
        return [media.url for media in self.attached_medias]
