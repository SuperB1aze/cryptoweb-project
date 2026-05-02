from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from pydantic import SecretStr
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from src.config import settings

def encode_jwt(
    payload: dict[str, Any],
    key: str = settings.auth_jwt.private_key_path.read_text(),
    passphrase: bytes | None = settings.auth_jwt.passphrase,
    algorithm: str = settings.auth_jwt.algorithm,
    expiration_time: int = settings.auth_jwt.access_token_expiration_time,
    expiration_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    time_now = datetime.now(timezone.utc)
    if expiration_timedelta:
        time_to_expire = time_now + expiration_timedelta
    else:
        time_to_expire = time_now + timedelta(minutes=expiration_time)
    to_encode.update(exp=time_to_expire, iat=time_now)

    private_key = serialization.load_pem_private_key(
        key.encode("utf-8"), password=passphrase, backend=default_backend()
    )
    if not isinstance(private_key, RSAPrivateKey):
        raise ValueError("JWT private key must be an RSA private key")

    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded

def decode_jwt(
    encoded: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict[str, Any]:
    decoded = jwt.decode(encoded, key=public_key, algorithms=[algorithm])
    if not isinstance(decoded, dict):
        raise ValueError("Invalid JWT payload")
    return decoded

def hash_password(password: str | SecretStr) -> str:
    if isinstance(password, SecretStr):
        password = password.get_secret_value()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def check_password(password: str | SecretStr, hashed_password: str) -> bool:
    if isinstance(password, SecretStr):
        password = password.get_secret_value()
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
