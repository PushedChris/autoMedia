import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from shared.models import GenericResponse, User

app = FastAPI(
    title="用户服务",
    description="用户管理微服务",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

users_db = {}


@app.post("/api/users", response_model=GenericResponse)
async def create_user(username: str, email: str):
    user_id = uuid.uuid4().hex
    user = User(id=user_id, username=username, email=email)
    users_db[user_id] = user
    return GenericResponse(
        status="ok", message="用户创建成功", data={"user": user.model_dump()}
    )


@app.get("/api/users/{user_id}", response_model=GenericResponse)
async def get_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    return GenericResponse(
        status="ok", message="获取成功", data={"user": users_db[user_id].model_dump()}
    )


@app.get("/health", response_model=GenericResponse)
async def health_check():
    return GenericResponse(
        status="ok", message="用户服务正常", data={"user_count": len(users_db)}
    )
