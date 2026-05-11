from uuid import uuid4
from urllib.parse import urlparse

from fastapi import HTTPException, UploadFile
from sqlalchemy import select

from src.config import settings
from src.database import async_session_factory
from src.infrastructure.db.media import AttachedMediasOrm, PFPsOrm
from src.infrastructure.db.models import PostsOrm, UsersOrm
from src.infrastructure.minioS3.minio import S3Client


class MediaServiceORM:
    MAX_POST_MEDIA_FILES = 10

    @staticmethod
    def get_storage_prefix() -> str:
        return "test" if settings.db.TEST_MODE else "main"

    @staticmethod
    async def upload_to_minio(
        owner_prefix: str,
        owner_id: int,
        file: UploadFile,
        images_only: bool = True,
    ) -> str:
        if images_only and (not file.content_type or not file.content_type.startswith("image/")):
            raise HTTPException(status_code=400, detail="Only image files are allowed")

        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        ext = ""
        if file.filename and "." in file.filename:
            ext = "." + file.filename.rsplit(".", 1)[-1].lower()
        object_name = f"{MediaServiceORM.get_storage_prefix()}/{owner_prefix}/{owner_id}/{uuid4().hex}{ext}"

        s3 = S3Client(
            access_key=settings.minio.access_key,
            secret_key=settings.minio.secret_key,
            endpoint_url=settings.minio.endpoint_url,
            bucket_name=settings.minio.bucket_name,
        )
        await s3.upload_bytes(file_bytes, object_name, file.content_type or "application/octet-stream")
        return s3.build_object_url(object_name, settings.minio.public_base_url)

    @staticmethod
    def extract_obj_name(url: str) -> str | None:
        path = urlparse(url).path.strip("/")
        prefix = f"{settings.minio.bucket_name}/"
        if not path.startswith(prefix):
            return None
        return path.removeprefix(prefix)

    @staticmethod
    async def upload_user_pfp(user_id: int, pfp_file: UploadFile | None) -> None:
        if pfp_file is None:
            return

        pfp_url = await MediaServiceORM.upload_to_minio("pfps", user_id, pfp_file)
        async with async_session_factory() as session:
            user = await session.get(UsersOrm, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            pfp = await session.scalar(select(PFPsOrm).where(PFPsOrm.user_id == user_id))
            if pfp is None:
                session.add(PFPsOrm(url=pfp_url, user_id=user_id))
            else:
                pfp.url = pfp_url
            await session.commit()

    @staticmethod
    async def attach_media(post_id: int, media_files: list[UploadFile] | None) -> None:
        if not media_files:
            return
        if len(media_files) > MediaServiceORM.MAX_POST_MEDIA_FILES:
            raise HTTPException(status_code=400, detail="You can attach up to 10 media files")

        async with async_session_factory() as session:
            post = await session.get(PostsOrm, post_id)
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")

            for media_file in media_files:
                media_url = await MediaServiceORM.upload_to_minio(
                    "posts",
                    post_id,
                    media_file,
                    images_only=False,
                )
                session.add(AttachedMediasOrm(url=media_url, post_id=post_id))

            await session.commit()

    @staticmethod
    async def delete_user_pfp(user_id: int) -> None:
        async with async_session_factory() as session:
            pfp = await session.scalar(select(PFPsOrm).where(PFPsOrm.user_id == user_id))
            if pfp is None:
                return
            object_name = MediaServiceORM.extract_obj_name(pfp.url)
            if object_name is None:
                return

        s3 = S3Client(
            access_key=settings.minio.access_key,
            secret_key=settings.minio.secret_key,
            endpoint_url=settings.minio.endpoint_url,
            bucket_name=settings.minio.bucket_name,
        )
        try:
            await s3.delete_object(object_name)
        except Exception:
            return
