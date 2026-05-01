import os
from pydantic_settings import BaseSettings


def strtobool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "on")


class Settings(BaseSettings):
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket_raw: str = os.getenv("MINIO_BUCKET_RAW", "raw")
    minio_bucket_processed: str = os.getenv("MINIO_BUCKET_PROCESSED", "processed")
    minio_bucket_output: str = os.getenv("MINIO_BUCKET_OUTPUT", "output")

    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/ai_platform")
    local_gpu_enabled: bool = strtobool(os.getenv("LOCAL_GPU_ENABLED", "false"))
    cloud_fallback_url: str = os.getenv("CLOUD_FALLBACK_URL", "")
    upload_prefix: str = os.getenv("UPLOAD_PREFIX", "uploads")
    task_prefix: str = os.getenv("TASK_PREFIX", "tasks")

    api_gateway_port: int = int(os.getenv("API_GATEWAY_PORT", "8000"))
    user_service_url: str = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
    image_service_url: str = os.getenv("IMAGE_SERVICE_URL", "http://image-service:8002")
    content_service_url: str = os.getenv("CONTENT_SERVICE_URL", "http://content-service:8003")
    task_service_url: str = os.getenv("TASK_SERVICE_URL", "http://task-service:8004")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
