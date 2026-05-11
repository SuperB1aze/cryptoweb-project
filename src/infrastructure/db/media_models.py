from typing import Annotated
from typing import TYPE_CHECKING

from infrastructure.db.base_model import Base, uuid_primary_key, created_at
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from infrastructure.db.main_models import UsersOrm, PostsOrm
    from infrastructure.db.reaction_models import CommentsOrm

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
    __table_args__ = (
        CheckConstraint(
            "(post_id IS NOT NULL AND comment_id IS NULL) OR (post_id IS NULL AND comment_id IS NOT NULL)",
            name="attached_medias_one_target",
        ),
    )

    post_id: Mapped[Annotated[int | None, mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)]]
    comment_id: Mapped[
        Annotated[int | None, mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)]
    ]

    post: Mapped["PostsOrm | None"] = relationship(back_populates="attached_medias")
    comment: Mapped["CommentsOrm | None"] = relationship(back_populates="attached_medias")
    repr_cols = ("id", "post_id", "comment_id", "created_at")
