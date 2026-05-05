from contextlib import asynccontextmanager
from aiobotocore.session import get_session

class S3Client:
    def __init__(self, access_key: str, secret_key: str, endpoint_url: str, bucket_name: str):
        self.config = {
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key,
            'endpoint_url': endpoint_url,
            'region_name': 'us-east-1'
        }
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url.rstrip("/")
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client('s3', **self.config) as client:
            yield client

    async def upload_bytes(self, content: bytes, object_name: str, content_type: str):
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=content,
                ContentType=content_type,
            )

    async def delete_object(self, object_name: str):
        async with self.get_client() as client:
            await client.delete_object(Bucket=self.bucket_name, Key=object_name)

    def build_object_url(self, object_name: str, public_base_url: str | None = None) -> str:
        base = (public_base_url or self.endpoint_url).rstrip("/")
        return f"{base}/{self.bucket_name}/{object_name}"
