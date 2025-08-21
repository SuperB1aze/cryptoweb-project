from pydantic import BaseModel, EmailStr, SecretStr

class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr

class TokenInfo(BaseModel):
    access_token: str
    token_type: str