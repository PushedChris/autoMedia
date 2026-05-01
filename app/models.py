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
