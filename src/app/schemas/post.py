from pydantic import BaseModel, Field
from src.app.schemas.user import UserDefaultInfoAddDTO
from datetime import datetime

class PostDefaultInfoAddDTO(BaseModel):
    text_content: str = Field(min_length=1, max_length=1000, description="Your post can only be from 1 to 1000 characters.")

    model_config = {
        "extra": "forbid",
        "from_attributes": True
    }

class PostPageInfoDTO(PostDefaultInfoAddDTO):
    created_at: datetime
    updated_at: datetime | None = None

class PostFullInfoDTO(PostPageInfoDTO):
    user: UserDefaultInfoAddDTO