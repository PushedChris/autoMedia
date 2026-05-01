import io
import asyncio
import uuid
from datetime import datetime

import httpx
from minio import Minio
from redis.asyncio import Redis

from app.config import settings


class MinIOService:
    def __init__(self, settings):
        endpoint = settings.minio_endpoint
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            endpoint = endpoint.split("//", 1)[1]
        host, port = endpoint.split(":", 1) if ":" in endpoint else (endpoint, "9000")
        self.client = Minio(
            f"{host}:{port}",
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False,
        )
        self.buckets = [
            settings.minio_bucket_raw,
            settings.minio_bucket_processed,
            settings.minio_bucket_output,
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


class AIService:
    async def analyze_image(self, bucket: str, object_name: str) -> dict:
        await asyncio.sleep(0.8)
        return {
            "object_name": object_name,
            "bucket": bucket,
            "content_tags": ["风景", "城市", "光影"],
            "style": "写实",
            "emotion": "宁静",
        }

    async def generate_copy(self, analysis: dict) -> dict:
        await asyncio.sleep(1.0)
        title = f"基于{analysis['style']}风格的爆款图文创作"
        body = (
            "这张图片展现了城市光影与自然融合的美感，" 
            "适合用于自媒体封面与广告文案。"
        )
        return {
            "title": title,
            "body": body,
            "tags": ["自媒体", "图文", "爆款", analysis["style"]],
        }

    async def optimize_style(self, copy: dict) -> dict:
        await asyncio.sleep(0.5)
        copy["optimized"] = True
        copy["platform_style"] = "头条/小红书/视频号"
        return copy

    async def cloud_fallback(self, analysis: dict) -> dict:
        if not settings.cloud_fallback_url:
            raise RuntimeError("未配置 CLOUD_FALLBACK_URL")
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                settings.cloud_fallback_url,
                json={"analysis": analysis},
            )
            resp.raise_for_status()
            return resp.json()


class TaskScheduler:
    def __init__(self, redis: Redis, minio_service: MinIOService):
        self.redis = redis
        self.minio_service = minio_service
        self.ai_service = AIService()
        self.task_prefix = settings.task_prefix

    async def create_task(self, bucket: str, object_name: str, pipeline: str = "default") -> str:
        task_id = uuid.uuid4().hex
        task_key = f"{self.task_prefix}:{task_id}"
        task_data = {
            "task_id": task_id,
            "bucket": bucket,
            "object_name": object_name,
            "pipeline": pipeline,
            "status": "pending",
            "progress": 0,
            "message": "等待执行",
            "created_at": datetime.utcnow().isoformat(),
        }
        await self.redis.hset(task_key, mapping=task_data)
        await self.redis.expire(task_key, 60 * 60 * 24)
        asyncio.create_task(self._run_task(task_id))
        return task_id

    async def get_status(self, task_id: str) -> dict | None:
        task_key = f"{self.task_prefix}:{task_id}"
        data = await self.redis.hgetall(task_key)
        return {k.decode(): v.decode() for k, v in data.items()} if data else None

    async def _run_task(self, task_id: str):
        task_key = f"{self.task_prefix}:{task_id}"
        await self.redis.hset(task_key, mapping={"status": "running", "progress": 10, "message": "开始处理"})
        task = await self.redis.hgetall(task_key)
        if not task:
            return

        bucket = task[b"bucket"].decode()
        object_name = task[b"object_name"].decode()
        use_local = settings.local_gpu_enabled

        if use_local:
            step = "local"
        else:
            step = "cloud"

        try:
            await self.redis.hset(task_key, mapping={"progress": 20, "message": f"调度到{step}节点"})
            analysis = await self.ai_service.analyze_image(bucket, object_name)
            await self.redis.hset(task_key, mapping={"progress": 45, "message": "图像理解完成"})

            generated = await self.ai_service.generate_copy(analysis)
            await self.redis.hset(task_key, mapping={"progress": 70, "message": "文案生成完成"})

            optimized = await self.ai_service.optimize_style(generated)
            await self.redis.hset(task_key, mapping={"progress": 85, "message": "风格优化完成"})

            result_object = f"{task_id}/result.json"
            result_bytes = str({"analysis": analysis, "copy": optimized}).encode("utf-8")
            self.minio_service.upload_bytes(
                settings.minio_bucket_output,
                result_object,
                result_bytes,
                content_type="application/json",
            )
            await self.redis.hset(task_key, mapping={"progress": 100, "status": "completed", "message": "任务完成", "result_object": result_object})
        except Exception as exc:
            await self.redis.hset(task_key, mapping={"status": "failed", "message": str(exc), "progress": 0})
