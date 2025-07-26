from pydantic import BaseModel, Field, EmailStr, field_validator

priveleges_values = ["User", "Mod", "Admin"]

class UserDefaultInfo(BaseModel):
    tag: str = Field(min_length=1, max_length=20, pattern=r'^[A-Za-z0-9_.]+$', description="Your tag can only be from 1 to 20 characters and contain English letters, numbers, underscores and dots.")
    name: str = Field(min_length=1, max_length=20, description="Your name can only be from 1 to 20 characters.")

    class Config:
        extra = "forbid"
         
class UserCreate(UserDefaultInfo):
    age: int = Field(ge=16, le=120, description="Your age can only be from 16 to 120 years old.")
    email: EmailStr
    password: str

class SuperUserCreate(UserCreate):
    role: str

    @field_validator("role")
    def role_validator(cls, profile_role):
        if profile_role not in priveleges_values:
            raise ValueError("This role does not exist")
        return profile_role

class UserBio(BaseModel):
    description: str | None = Field(max_length=500, description="Your description can only be up to 500 characters.")
    city: str | None
    country: str | None

users_list_test = [
    {"id": 1, "tag": "dev", "name": "that dev guy", "email": "amogus@sussy.com", "password":"12345", "age": "22", "role": "User"},
    {"id": 2, "tag": "randomuser", "name": "normie", "email": "yoyo@sus.com", "password":"12345", "role":"Mod"},
    {"id": 3, "tag": "anotheruser", "name": "bro", "email": "yolo@sus.com", "password":"12345", "role":"User"}
]