import uuid
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.config import settings
from app.models import GenericResponse, TaskCreateRequest, TaskStatusResponse, UploadResponse
from app.services import MinIOService, TaskScheduler

app = FastAPI(
    title="AI 图文创作平台",
    description="本地 GPU + 云端调度混合架构 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    app.state.minio = MinIOService(settings)
    await app.state.minio.ensure_buckets()
    app.state.redis = await Redis.from_url(settings.redis_url)
    app.state.scheduler = TaskScheduler(app.state.redis, app.state.minio)


@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, "redis"):
        await app.state.redis.close()


@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    data = await file.read()
    object_name = f"{uuid.uuid4().hex}/{file.filename}"
    try:
        app.state.minio.upload_bytes(settings.minio_bucket_raw, object_name, data, file.content_type)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"上传失败: {exc}")

    task_id = await app.state.scheduler.create_task(settings.minio_bucket_raw, object_name)
    return UploadResponse(
        task_id=task_id,
        object_name=object_name,
        bucket=settings.minio_bucket_raw,
        message="文件已上传，已创建分析任务",
    )


@app.post("/api/task", response_model=GenericResponse)
async def create_task(request: TaskCreateRequest):
    if request.bucket not in [settings.minio_bucket_raw, settings.minio_bucket_processed, settings.minio_bucket_output]:
        raise HTTPException(status_code=400, detail="bucket 参数无效")
    task_id = await app.state.scheduler.create_task(request.bucket, request.object_name, request.pipeline)
    return GenericResponse(status="ok", message="任务已创建", data={"task_id": task_id})


@app.get("/api/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    task = await app.state.scheduler.get_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskStatusResponse(
        task_id=task_id,
        status=task.get("status", "unknown"),
        progress=int(task.get("progress", 0)),
        message=task.get("message"),
        result={
            "result_object": task.get("result_object"),
        } if task.get("result_object") else None,
    )


@app.get("/health", response_model=GenericResponse)
async def health_check():
    return GenericResponse(status="ok", message="服务正常", data={"local_gpu_enabled": settings.local_gpu_enabled})
