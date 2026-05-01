import uuid
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from shared.config import settings
from shared.models import GenericResponse, UploadResponse
from shared.minio_service import MinIOService

app = FastAPI(
    title="图片处理服务",
    description="图片上传与处理微服务",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

minio_service = None
redis = None


@app.on_event("startup")
async def startup_event():
    global minio_service, redis
    minio_service = MinIOService(settings)
    await minio_service.ensure_buckets()
    redis = await Redis.from_url(settings.redis_url)


@app.on_event("shutdown")
async def shutdown_event():
    if redis:
        await redis.close()


@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    data = await file.read()
    object_name = f"{uuid.uuid4().hex}/{file.filename}"
    try:
        minio_service.upload_bytes(settings.minio_bucket_raw, object_name, data, file.content_type)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"上传失败: {exc}")

    return UploadResponse(
        task_id="",
        object_name=object_name,
        bucket=settings.minio_bucket_raw,
        message="文件已上传",
    )


@app.get("/api/presigned/{bucket}/{object_name:path}", response_model=GenericResponse)
async def get_presigned_url(bucket: str, object_name: str):
    try:
        url = minio_service.presigned_url(bucket, object_name)
        return GenericResponse(status="ok", message="获取成功", data={"url": url})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health", response_model=GenericResponse)
async def health_check():
    return GenericResponse(status="ok", message="图片服务正常")
