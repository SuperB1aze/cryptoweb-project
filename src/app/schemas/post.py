from pydantic import BaseModel, Field
from src.app.schemas.user import UserDefaultInfoAddDTO
from infrastructure.db.main_models import Role
from datetime import datetime

class PostIDDTO(BaseModel):
    id: int

class PostDefaultInfoAddDTO(BaseModel):
    text_content: str = Field(min_length=1,
                              max_length=1000,
                              description="Your post can only be from 1 to 1000 characters.")

    model_config = {
        "extra": "forbid",
        "from_attributes": True
    }

class CommentDefaultInfoAddDTO(BaseModel):
    text_content: str = Field(min_length=1,
                              max_length=300,
                              description="Your comment can only be from 1 to 300 characters.")

    model_config = {
        "extra": "forbid",
        "from_attributes": True
    }

class PostPageInfoDTO(PostIDDTO, PostDefaultInfoAddDTO):
    media_urls: list[str] = Field(default_factory=list, description="Attached media URLs.")
    likes_count: int = Field(default=0, ge=0, description="Number of likes on the post.")
    created_at: datetime
    updated_at: datetime | None = None

class PostFullInfoDTO(PostPageInfoDTO):
    user: UserDefaultInfoAddDTO

class CommentDTO(BaseModel):
    id: int
    user: UserDefaultInfoAddDTO
    text_content: str = Field(min_length=1,
                              max_length=300,
                              description="Your post can only be from 1 to 300 characters.")
    media_urls: list[str] = Field(default_factory=list, description="Attached media URLs.")
    likes_count: int = Field(default=0, ge=0, description="Number of likes on the comment.")
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {
        "extra": "forbid",
        "from_attributes": True
    }

class PostReactionsInfoDTO(PostFullInfoDTO):
    comments_list: list[CommentDTO] = Field(default_factory=list, description="List of comments on the post.")

class PostOwnershipDTO(BaseModel):
    is_owner: bool
    role: Role
