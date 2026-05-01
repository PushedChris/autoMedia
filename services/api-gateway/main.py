import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from shared.config import settings
from shared.models import GenericResponse

app = FastAPI(
    title="AI 图文创作平台 - API Gateway",
    description="API 网关，统一服务入口",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api_route("/api/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def api_proxy(service_name: str, path: str, request: Request):
    service_urls = {
        "user": settings.user_service_url,
        "image": settings.image_service_url,
        "content": settings.content_service_url,
        "task": settings.task_service_url,
    }

    if service_name not in service_urls:
        raise HTTPException(status_code=404, detail=f"服务 {service_name} 不存在")

    target_url = f"{service_urls[service_name]}/api/{path}"

    body = await request.body() if request.method in ["POST", "PUT"] else None

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=dict(request.headers),
            params=dict(request.query_params),
            content=body,
            stream=True,
        )
        return StreamingResponse(
            response.aiter_bytes(),
            status_code=response.status_code,
            headers=dict(response.headers),
        )


@app.get("/health", response_model=GenericResponse)
async def health_check():
    return GenericResponse(
        status="ok",
        message="API Gateway 正常",
        data={
            "user_service": settings.user_service_url,
            "image_service": settings.image_service_url,
            "content_service": settings.content_service_url,
            "task_service": settings.task_service_url,
        },
    )
