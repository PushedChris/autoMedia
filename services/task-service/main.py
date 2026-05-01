import asyncio
import uuid
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from shared.config import settings
from shared.minio_service import MinIOService
from shared.models import GenericResponse, TaskCreateRequest, TaskStatusResponse

app = FastAPI(
    title="任务调度服务",
    description="任务管理与调度微服务",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = None
minio_service = None


@app.on_event("startup")
async def startup_event():
    global redis, minio_service
    redis = await Redis.from_url(settings.redis_url)
    minio_service = MinIOService(settings)
    await minio_service.ensure_buckets()


@app.on_event("shutdown")
async def shutdown_event():
    if redis:
        await redis.close()


@app.post("/api/task", response_model=GenericResponse)
async def create_task(request: TaskCreateRequest):
    if request.bucket not in [
        settings.minio_bucket_raw,
        settings.minio_bucket_processed,
        settings.minio_bucket_output,
    ]:
        raise HTTPException(status_code=400, detail="bucket 参数无效")

    task_id = uuid.uuid4().hex
    task_key = f"{settings.task_prefix}:{task_id}"
    task_data = {
        "task_id": task_id,
        "bucket": request.bucket,
        "object_name": request.object_name,
        "pipeline": request.pipeline,
        "status": "pending",
        "progress": 0,
        "message": "等待执行",
        "created_at": datetime.utcnow().isoformat(),
    }
    await redis.hset(task_key, mapping=task_data)
    await redis.expire(task_key, 60 * 60 * 24)
    asyncio.create_task(run_task(task_id))
    return GenericResponse(status="ok", message="任务已创建", data={"task_id": task_id})


@app.get("/api/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    task_key = f"{settings.task_prefix}:{task_id}"
    data = await redis.hgetall(task_key)
    if not data:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = {k.decode(): v.decode() for k, v in data.items()}
    return TaskStatusResponse(
        task_id=task_id,
        status=task.get("status", "unknown"),
        progress=int(task.get("progress", 0)),
        message=task.get("message"),
        result=(
            {
                "result_object": task.get("result_object"),
            }
            if task.get("result_object")
            else None
        ),
    )


async def run_task(task_id: str):
    task_key = f"{settings.task_prefix}:{task_id}"
    await redis.hset(task_key, mapping={"status": "running", "progress": 10, "message": "开始处理"})
    task = await redis.hgetall(task_key)
    if not task:
        return

    bucket = task[b"bucket"].decode()
    object_name = task[b"object_name"].decode()

    try:
        await redis.hset(task_key, mapping={"progress": 20, "message": "调用图片分析"})

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{settings.content_service_url}/api/analyze",
                params={"bucket": bucket, "object_name": object_name},
            )
            analysis = resp.json()["data"]["analysis"]

        await redis.hset(task_key, mapping={"progress": 45, "message": "图像理解完成"})

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{settings.content_service_url}/api/generate",
                json=analysis,
            )
            generated = resp.json()["data"]["copy"]

        await redis.hset(task_key, mapping={"progress": 70, "message": "文案生成完成"})

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{settings.content_service_url}/api/optimize",
                json=generated,
            )
            optimized = resp.json()["data"]["copy"]

        await redis.hset(task_key, mapping={"progress": 85, "message": "风格优化完成"})

        result_object = f"{task_id}/result.json"
        result_bytes = str({"analysis": analysis, "copy": optimized}).encode("utf-8")
        minio_service.upload_bytes(
            settings.minio_bucket_output,
            result_object,
            result_bytes,
            content_type="application/json",
        )
        await redis.hset(
            task_key,
            mapping={
                "progress": 100,
                "status": "completed",
                "message": "任务完成",
                "result_object": result_object,
            },
        )
    except Exception as exc:
        await redis.hset(task_key, mapping={"status": "failed", "message": str(exc), "progress": 0})


@app.get("/health", response_model=GenericResponse)
async def health_check():
    return GenericResponse(status="ok", message="任务调度服务正常")
