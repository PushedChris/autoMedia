import io
from minio import Minio

from shared.config import settings


class MinIOService:
    def __init__(self, settings_obj=None):
        s = settings_obj or settings
        endpoint = s.minio_endpoint
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            endpoint = endpoint.split("//", 1)[1]
        host, port = endpoint.split(":", 1) if ":" in endpoint else (endpoint, "9000")
        self.client = Minio(
            f"{host}:{port}",
            access_key=s.minio_access_key,
            secret_key=s.minio_secret_key,
            secure=False,
        )
        self.buckets = [
            s.minio_bucket_raw,
            s.minio_bucket_processed,
            s.minio_bucket_output,
        ]

    async def ensure_buckets(self):
        for bucket in self.buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)

    def upload_bytes(self, bucket: str, object_name: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        self.client.put_object(
            bucket,
            object_name,
            data=io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        return object_name

    def presigned_url(self, bucket: str, object_name: str, expires: int = 3600) -> str:
        return self.client.presigned_get_object(bucket, object_name, expires=expires)

    def copy_object(self, source_bucket: str, object_name: str, dest_bucket: str, dest_object_name: str) -> None:
        self.client.copy_object(
            dest_bucket,
            dest_object_name,
            f"{source_bucket}/{object_name}",
        )
