from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pathlib import Path

import os
from dotenv import load_dotenv
load_dotenv()

class DB_Settings(BaseSettings):
    DB_HOST: str | None = os.getenv("DB_HOST")
    DB_PORT: int | None = int(os.getenv("DB_PORT"))
    DB_USER: str | None = os.getenv("DB_USER")
    DB_PASS: str | None = os.getenv("DB_PASS")
    DB_NAME: str | None = os.getenv("DB_NAME")

    DB_MIGRATION_USER: str | None = os.getenv("DB_MIGRATION_USER")
    DB_MIGRATION_PASS: str | None = os.getenv("DB_MIGRATION_PASS")

    TEST_MODE: int | None = int(os.getenv("TEST_MODE"))
    DB_TEST_HOST: str | None = os.getenv("DB_TEST_HOST")
    DB_TEST_USER: str | None = os.getenv("DB_TEST_USER")
    DB_TEST_PASS: str | None = os.getenv("DB_TEST_PASS")
    DB_TEST_PORT: int | None = int(os.getenv("DB_TEST_PORT"))
    DB_TEST_NAME: str | None = os.getenv("DB_TEST_NAME")

    @property
    def DATABASE_URL_asyncpg_testing(self):
        return f"postgresql+asyncpg://{self.DB_TEST_USER}:{self.DB_TEST_PASS}@{self.DB_TEST_HOST}:{self.DB_TEST_PORT}/{self.DB_TEST_NAME}"

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}" if self.TEST_MODE != 1 else self.DATABASE_URL_asyncpg_testing
    
    @property
    def DATABASE_URL_asyncpg_migrations(self):
        return f"postgresql+asyncpg://{self.DB_MIGRATION_USER}:{self.DB_MIGRATION_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}" if self.TEST_MODE != 1 else self.DATABASE_URL_asyncpg_testing
    

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