import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.models import GenericResponse, ImageAnalysis, GeneratedCopy

app = FastAPI(
    title="内容生成服务",
    description="AI 内容生成微服务",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze", response_model=GenericResponse)
async def analyze_image(bucket: str, object_name: str):
    await asyncio.sleep(0.8)
    analysis = ImageAnalysis(
        object_name=object_name,
        bucket=bucket,
        content_tags=["风景", "城市", "光影"],
        style="写实",
        emotion="宁静",
    )
    return GenericResponse(status="ok", message="分析完成", data={"analysis": analysis.model_dump()})


@app.post("/api/generate", response_model=GenericResponse)
async def generate_copy(analysis: dict):
    await asyncio.sleep(1.0)
    title = f"基于{analysis.get('style', '通用')}风格的爆款图文创作"
    body = (
        "这张图片展现了城市光影与自然融合的美感，" 
        "适合用于自媒体封面与广告文案。"
    )
    copy = GeneratedCopy(
        title=title,
        body=body,
        tags=["自媒体", "图文", "爆款", analysis.get("style", "通用")],
    )
    return GenericResponse(status="ok", message="生成完成", data={"copy": copy.model_dump()})


@app.post("/api/optimize", response_model=GenericResponse)
async def optimize_style(copy: dict):
    await asyncio.sleep(0.5)
    copy["optimized"] = True
    copy["platform_style"] = "头条/小红书/视频号"
    return GenericResponse(status="ok", message="优化完成", data={"copy": copy})


@app.get("/health", response_model=GenericResponse)
async def health_check():
    return GenericResponse(status="ok", message="内容生成服务正常", data={"local_gpu": settings.local_gpu_enabled})
