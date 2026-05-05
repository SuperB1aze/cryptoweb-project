import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


def get_required_int_env(name: str) -> int:
    return int(get_required_env(name))


def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")


def get_env_any(*names: str, default: str | None = None) -> str:
    for name in names:
        value = os.getenv(name)
        if value is not None:
            return value
    if default is not None:
        return default
    raise RuntimeError(f"Environment variable one of {names} is required")


class DBSettings(BaseSettings):
    DB_HOST: str = get_required_env("DB_HOST")
    DB_PORT: int = get_required_int_env("DB_PORT")
    DB_USER: str = get_required_env("DB_USER")
    DB_PASS: str = get_required_env("DB_PASS")
    DB_NAME: str = get_required_env("DB_NAME")

    DB_MIGRATION_USER: str = get_required_env("DB_MIGRATION_USER")
    DB_MIGRATION_PASS: str = get_required_env("DB_MIGRATION_PASS")

    TEST_MODE: int = get_required_int_env("TEST_MODE")
    DB_TEST_HOST: str = get_required_env("DB_TEST_HOST")
    DB_TEST_USER: str = get_required_env("DB_TEST_USER")
    DB_TEST_PASS: str = get_required_env("DB_TEST_PASS")
    DB_TEST_PORT: int = get_required_int_env("DB_TEST_PORT")
    DB_TEST_NAME: str = get_required_env("DB_TEST_NAME")

    @property
    def DATABASE_URL_asyncpg_testing(self) -> str:
        return f"postgresql+asyncpg://{self.DB_TEST_USER}:{self.DB_TEST_PASS}@{self.DB_TEST_HOST}:{self.DB_TEST_PORT}/{self.DB_TEST_NAME}"

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}" if self.TEST_MODE != 1 else self.DATABASE_URL_asyncpg_testing
    
    @property
    def DATABASE_URL_asyncpg_migrations(self) -> str:
        return f"postgresql+asyncpg://{self.DB_MIGRATION_USER}:{self.DB_MIGRATION_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}" if self.TEST_MODE != 1 else self.DATABASE_URL_asyncpg_testing
    

BASE_DIR = Path(__file__).resolve().parent.parent
PRIVATE_KEY_PATH = BASE_DIR / "certs" / "private.pem"
PUBLIC_KEY_PATH = BASE_DIR / "certs" / "public.pem"

class AuthJWT(BaseModel):
    private_key_path: Path = PRIVATE_KEY_PATH
    public_key_path: Path = PUBLIC_KEY_PATH
    passphrase: bytes = get_required_env("PASSPHRASE").encode("utf-8")
    algorithm: str = "RS256"
    access_token_expiration_time: int = 15
    refresh_token_expiration_days: int = 30
    refresh_cookie_secure: bool = get_bool_env("REFRESH_COOKIE_SECURE")


class MinIOSettings(BaseSettings):
    endpoint_url: str = get_env_any("MINIO_ENDPOINT_URL", "S3_ENDPOINT", default="http://localhost:9000")
    access_key: str = get_env_any("MINIO_ACCESS_KEY", "S3_ACCESS_KEY", default="minioadmin")
    secret_key: str = get_env_any("MINIO_SECRET_KEY", "S3_SECRET_KEY", default="minioadmin")
    bucket_name: str = get_env_any("MINIO_BUCKET_NAME", "S3_BUCKET", default="media")
    public_base_url: str = get_env_any("MINIO_PUBLIC_BASE_URL", "S3_ENDPOINT", default="http://localhost:9000")


class Settings(BaseSettings):
    db: DBSettings = Field(default_factory=DBSettings)
    auth_jwt: AuthJWT = Field(default_factory=AuthJWT)
    minio: MinIOSettings = Field(default_factory=MinIOSettings)

settings = Settings()
