from typing import Annotated
from typing import TYPE_CHECKING

from src.infrastructure.db.base import Base, uuid_primary_key, created_at
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.infrastructure.db.models import UsersOrm, PostsOrm

class MediaOrm(Base):
    __abstract__ = True

    id: Mapped[uuid_primary_key]
    created_at: Mapped[created_at]
    url: Mapped[str]

class PFPsOrm(MediaOrm):
    __tablename__ = "pfps"

    user_id: Mapped[Annotated[int, mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)]]

    user: Mapped["UsersOrm"] = relationship(back_populates="pfp")
    repr_cols = ("id", "user_id", "created_at")

class AttachedMediasOrm(MediaOrm):
    __tablename__ = "attached_medias"

    post_id: Mapped[Annotated[int, mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)]]

    post: Mapped["PostsOrm"] = relationship(back_populates="attached_medias")
    repr_cols = ("id", "post_id", "created_at")
