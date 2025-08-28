from pydantic import BaseModel, Field, EmailStr, SecretStr
from src.infrastructure.db.models import Role
from src.app.schemas.auth import TokenInfo
from datetime import datetime

class UserDefaultInfoAddDTO(BaseModel):
    tag: str = Field(min_length=1, max_length=20, pattern=r'^[A-Za-z0-9_.]+$', description="Your tag can only be from 1 to 20 characters and contain English letters, numbers, underscores and dots.")
    name: str = Field(min_length=1, max_length=20, description="Your name can only be from 1 to 20 characters.")

    model_config = {
        "extra": "forbid",
        "from_attributes": True
    }

class UserAgeDTO(BaseModel):
    age: int = Field(ge=16, le=120, description="Your age can only be from 16 to 120 years old.")
         
class UserCreateAddDTO(UserAgeDTO, UserDefaultInfoAddDTO):
    email: EmailStr
    password: SecretStr

class UserBioAddDTO(BaseModel):
    description: str | None = Field(max_length=500, description="Your description can only be up to 500 characters.")
    city: str | None
    country: str | None

class UserFullInfoDTO(UserBioAddDTO, UserAgeDTO, UserDefaultInfoAddDTO):
    role: Role
    created_at: datetime

class UserFullInfoWithTokenDTO(BaseModel):
    user: UserFullInfoDTO
    token: TokenInfo | None