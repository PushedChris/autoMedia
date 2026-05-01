from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    task_id: str
    object_name: str
    bucket: str
    message: str


class TaskCreateRequest(BaseModel):
    object_name: str = Field(..., description="MinIO 中已上传文件对象名")
    bucket: str = Field(..., description="文件所在 Bucket")
    pipeline: str = Field("default", description="任务处理管线")


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str | None = None
    result: dict | None = None


class GenericResponse(BaseModel):
    status: str
    message: str
    data: dict | None = None


class User(BaseModel):
    id: str
    username: str
    email: str


class ImageAnalysis(BaseModel):
    object_name: str
    bucket: str
    content_tags: list[str]
    style: str
    emotion: str


class GeneratedCopy(BaseModel):
    title: str
    body: str
    tags: list[str]
    optimized: bool = False
    platform_style: str = ""
