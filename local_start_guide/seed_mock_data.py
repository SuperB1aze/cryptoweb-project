import asyncio
import sys
from pathlib import Path

import bcrypt
from sqlalchemy import select

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.database import async_session_factory
from src.infrastructure.db.models import PostsOrm, Role, UsersOrm


MOCK_PASSWORD = "password123"

MOCK_USERS = [
    {
        "tag": "admin",
        "name": "Admin",
        "age": 28,
        "email": "admin@example.com",
        "role": Role.admin,
        "city": "Moscow",
        "country": "Russia",
        "description": "Local admin account for development.",
    },
    {
        "tag": "alice.dev",
        "name": "Alice",
        "age": 24,
        "email": "alice@example.com",
        "role": Role.user,
        "city": "Saint Petersburg",
        "country": "Russia",
        "description": "Writes about backend experiments.",
    },
    {
        "tag": "bob_ops",
        "name": "Bob",
        "age": 31,
        "email": "bob@example.com",
        "role": Role.mod,
        "city": "Kazan",
        "country": "Russia",
        "description": "Moderates demo content.",
    },
]

MOCK_POSTS = {
    "admin@example.com": [
        "Welcome to the local Cryptoweb demo database.",
        "Use these accounts only for development and smoke testing.",
    ],
    "alice@example.com": [
        "First local post: FastAPI plus async SQLAlchemy is alive.",
        "Mock data makes API checks much nicer.",
    ],
    "bob@example.com": [
        "Moderator note: seeded posts are safe to delete and recreate.",
    ],
}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def seed() -> None:
    async with async_session_factory() as session:
        users_by_email: dict[str, UsersOrm] = {}

        for user_data in MOCK_USERS:
            result = await session.execute(
                select(UsersOrm).where(UsersOrm.email == user_data["email"])
            )
            user = result.scalar_one_or_none()

            if user is None:
                user = UsersOrm(
                    **user_data,
                    password=hash_password(MOCK_PASSWORD),
                    is_active=True,
                )
                session.add(user)
                await session.flush()

            users_by_email[user.email] = user

        for email, posts in MOCK_POSTS.items():
            user = users_by_email[email]
            for text_content in posts:
                result = await session.execute(
                    select(PostsOrm).where(
                        PostsOrm.user_id == user.id,
                        PostsOrm.text_content == text_content,
                    )
                )
                if result.scalar_one_or_none() is None:
                    session.add(PostsOrm(user_id=user.id, text_content=text_content))

        await session.commit()

    print("Mock data seeded.")
    print(f"Demo password for all seeded users: {MOCK_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
