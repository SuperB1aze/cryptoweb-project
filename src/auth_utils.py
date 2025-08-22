import jwt, bcrypt
from pydantic import SecretStr
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from src.config import settings
from datetime import datetime, timedelta, timezone

def encode_jwt(payload: dict, 
               key: str = settings.auth_jwt.private_key_path.read_text(), 
               passphrase: str = settings.auth_jwt.passphrase, 
               algorithm: str = settings.auth_jwt.algorithm,
               expiration_time: int = settings.auth_jwt.access_token_expiration_time,
               expiration_timedelta: timedelta | None = None
               ):
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
    encoded = jwt.encode(to_encode, private_key, algorithm)
    return encoded

def decode_jwt(encoded: str | bytes, 
               public_key: str = settings.auth_jwt.public_key_path.read_text(), 
               algorithm: str = settings.auth_jwt.algorithm
               ):
    decoded = jwt.decode(encoded, key=public_key, algorithms=[algorithm])
    return decoded

def hash_password(password: str | SecretStr):
    if isinstance(password, SecretStr):
        password = password.get_secret_value()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def check_password(password: str | SecretStr,
                   hashed_password: str):
    if isinstance(password, SecretStr):
        password = password.get_secret_value()
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))