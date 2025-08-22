from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path

import os
from dotenv import load_dotenv
load_dotenv()

class DB_Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

db_settings = DB_Settings()  # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent
PRIVATE_KEY_PATH = BASE_DIR / "certs" / "private.pem"
PUBLIC_KEY_PATH = BASE_DIR / "certs" / "public.pem"

class AuthJWT(BaseModel):
    private_key_path: Path = PRIVATE_KEY_PATH
    public_key_path: Path = PUBLIC_KEY_PATH
    passphrase: bytes = os.getenv("PASSPHRASE").encode("utf-8")
    algorithm: str = "RS256"
    access_token_expiration_time: int = 15


class Settings(BaseSettings):
    db: DB_Settings = DB_Settings() # type: ignore
    auth_jwt: AuthJWT = AuthJWT()

settings = Settings()