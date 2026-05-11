from typing import Annotated, TYPE_CHECKING
from infrastructure.db.base_model import Base, int_primary_key, created_at, updated_at

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from infrastructure.db.main_models import UsersOrm, PostsOrm
    from infrastructure.db.media_models import AttachedMediasOrm

class LikesOrm(Base):
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="unique_like_per_user_post"),
        UniqueConstraint("user_id", "comment_id", name="unique_like_per_user_comment"),
        CheckConstraint(
            "(post_id IS NOT NULL AND comment_id IS NULL) OR (post_id IS NULL AND comment_id IS NOT NULL)",
            name="likes_one_target",
        ),
    )

    id: Mapped[int_primary_key]
    user_id: Mapped[Annotated[int, mapped_column(ForeignKey("users.id", ondelete = "CASCADE"))]]
    post_id: Mapped[Annotated[int | None, mapped_column(ForeignKey("posts.id", ondelete = "CASCADE"), nullable=True)]]
    comment_id: Mapped[
        Annotated[int | None, mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)]
    ]
    created_at: Mapped[created_at]

    user: Mapped["UsersOrm"] = relationship(back_populates="likes", passive_deletes=True)
    post: Mapped["PostsOrm | None"] = relationship(back_populates="likes", passive_deletes=True)
    comment: Mapped["CommentsOrm | None"] = relationship(back_populates="likes", passive_deletes=True)

    repr_cols = ("id", "user_id", "post_id", "comment_id")

class CommentsOrm(Base):
    __tablename__ = "comments"

    id: Mapped[int_primary_key]
    user_id: Mapped[Annotated[int, mapped_column(ForeignKey("users.id", ondelete = "CASCADE"))]]
    post_id: Mapped[Annotated[int, mapped_column(ForeignKey("posts.id", ondelete = "CASCADE"))]]
    text_content: Mapped[Annotated[str, mapped_column(String(300), nullable=False)]]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at | None]

    user: Mapped["UsersOrm"] = relationship(back_populates="comments", passive_deletes=True)
    post: Mapped["PostsOrm"] = relationship(back_populates="comments", passive_deletes=True)
    attached_medias: Mapped[list["AttachedMediasOrm"]] = relationship(
        back_populates="comment",
        passive_deletes=True,
    )
    likes: Mapped[list["LikesOrm"]] = relationship(back_populates="comment", passive_deletes=True)
    repr_cols = ("id", "user_id", "post_id")

    @property
    def media_urls(self) -> list[str]:
        if not self.attached_medias:
            return []
        return [media.url for media in self.attached_medias]

    @property
    def likes_count(self) -> int:
        return len(self.likes) if self.likes else 0
