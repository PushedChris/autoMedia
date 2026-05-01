# LangChain k3s AI 图文创作平台

本项目基于 `k3s + 本地 GPU + 云端调度 + MinIO OSS` 构建混合部署架构。

## 目录
- `ARCHITECTURE.md`：架构说明
- `app/`：FastAPI 服务代码
- `k8s/`：k3s 部署模板
- `docker-compose.yml`：本地开发环境
- `scripts/setup_minio_buckets.sh`：MinIO Bucket 初始化

## 快速开始

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 本地运行：
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. 使用 `docker-compose` 启动基础服务：
   ```bash
   docker-compose up -d
   ```
4. 初始化 MinIO Buckets：
   ```bash
   bash scripts/setup_minio_buckets.sh
   ```

## 目录结构

- `app/main.py`：API 入口
- `app/services.py`：MinIO、Redis、AI 任务调度实现
- `k8s/`：k3s 部署清单

## 环境配置

通过环境变量配置：
- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET_RAW`
- `MINIO_BUCKET_PROCESSED`
- `MINIO_BUCKET_OUTPUT`
- `REDIS_URL`
- `DATABASE_URL`
- `LOCAL_GPU_ENABLED`

## 说明

本项目提供一个商用级混合调度架构示例，适合用于本地 GPU 快速推理与云端弹性调度场景。