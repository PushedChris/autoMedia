# 构建和部署指南

## 🏗️ 工程架构

### 系统架构图

```
                    ┌───────────────┐
                    │   用户浏览器  │
                    └───────┬───────┘
                            │
                    ┌───────▼────────┐
                    │  API Gateway  │ (端口: 18000)
                    │  (18000->8000) │
                    └─┬──────┬───────┘
                      │      │
         ┌────────────┴──────┴─────────────┐
         │                                 │
    ┌────▼─────┐  ┌───────▼──────┐  ┌─────▼──────┐
    │User      │  │Image         │  │Task        │
    │Service   │  │Service       │  │Service     │
    │(18001)   │  │(18002)       │  │(18004)     │
    └──────────┘  └───────┬──────┘  └─────┬──────┘
                           │              │
                    ┌──────▼───────┐     │
                    │Content      │     │
                    │Service      │     │
                    │(18003)      │     │
                    └──────┬───────┘     │
                           │             │
         ┌─────────────────┼─────────────┼─────────────┐
         │                 │             │             │
    ┌────▼────┐      ┌────▼──────┐ ┌──▼────┐   ┌─────▼─────┐
    │  MinIO  │      │  PostgreSQL │ │ Redis │   │   AI      │
    │(19000) │      │  (15432)   │ │(16379)│   │(本地/云端)│
    └─────────┘      └───────────┘ └───────┘   └───────────┘
```

### 微服务说明

| 服务名称 | 端口 | 功能描述 |
|---------|------|---------|
| **API Gateway** | 18000 | API 网关，统一请求入口和路由转发 |
| **User Service** | 18001 | 用户管理服务，处理用户注册、登录等 |
| **Image Service** | 18002 | 图片服务，处理图片上传、存储和预签名 URL |
| **Content Service** | 18003 | AI 内容生成服务，处理图片分析、文案生成 |
| **Task Service** | 18004 | 任务调度服务，管理异步任务的创建和状态 |

### 基础设施

| 组件 | 端口 | 用途 |
|-----|------|-----|
| **MinIO** | 19000/19001 | 对象存储，存储原始图片、处理结果、输出文件 |
| **PostgreSQL** | 15432 | 关系型数据库，存储业务数据 |
| **Redis** | 16379 | 缓存和消息队列，存储任务状态和缓存 |

---

## ⚙️ 配置参数说明

### MinIO 配置

| 参数名 | 默认值 | 说明 |
|--------|--------|-----|
| `MINIO_ENDPOINT` | minio:9000 | MinIO 服务地址 (容器内) |
| `MINIO_ACCESS_KEY` | minioadmin | MinIO 访问密钥 |
| `MINIO_SECRET_KEY` | minioadmin | MinIO 秘密密钥 |
| `MINIO_BUCKET_RAW` | raw | 原始图片存储 Bucket |
| `MINIO_BUCKET_PROCESSED` | processed | 处理结果存储 Bucket |
| `MINIO_BUCKET_OUTPUT` | output | 最终输出存储 Bucket |

### 数据库配置

| 参数名 | 默认值 | 说明 |
|--------|--------|-----|
| `DATABASE_URL` | postgresql://postgres:postgres@postgres:5432/ai_platform | PostgreSQL 数据库连接地址 |

### Redis 配置

| 参数名 | 默认值 | 说明 |
|--------|--------|-----|
| `REDIS_URL` | redis://redis:6379/0 | Redis 连接地址 |

### AI 配置

| 参数名 | 默认值 | 说明 |
|--------|--------|-----|
| `LOCAL_GPU_ENABLED` | true | 是否启用本地 GPU 推理 |
| `CLOUD_FALLBACK_URL` | (空) | 云端 AI 服务的回退地址 |

### 服务间通信配置

| 参数名 | 默认值 | 说明 |
|--------|--------|-----|
| `USER_SERVICE_URL` | http://user-service:8001 | 用户服务地址 |
| `IMAGE_SERVICE_URL` | http://image-service:8002 | 图片服务地址 |
| `CONTENT_SERVICE_URL` | http://content-service:8003 | 内容服务地址 |
| `TASK_SERVICE_URL` | http://task-service:8004 | 任务服务地址 |

### 其他配置

| 参数名 | 默认值 | 说明 |
|--------|--------|-----|
| `UPLOAD_PREFIX` | uploads | 上传文件前缀 |
| `TASK_PREFIX` | tasks | 任务键前缀 |

---

## 📦 本地开发

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 停止并删除数据卷 (清空数据)
docker-compose down -v
```

### 手动构建单个服务

```bash
# 从项目根目录构建
cd /Users/cchrishuang/Desktop/project/pyproject/langchain-k3s-search

# 构建 API Gateway
docker build -f services/api-gateway/Dockerfile -t api-gateway:latest .

# 构建 User Service
docker build -f services/user-service/Dockerfile -t user-service:latest .

# 构建 Image Service
docker build -f services/image-service/Dockerfile -t image-service:latest .

# 构建 Content Service
docker build -f services/content-service/Dockerfile -t content-service:latest .

# 构建 Task Service
docker build -f services/task-service/Dockerfile -t task-service:latest .
```

---

## ☸️ Kubernetes / K3s 部署

### 项目结构 (Kustomize)

```
k8s/
├── base/                    # 基础配置 (所有环境共享)
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── minio.yaml
│   ├── postgres.yaml
│   ├── redis.yaml
│   ├── user-service.yaml
│   ├── image-service.yaml
│   ├── content-service.yaml
│   ├── task-service.yaml
│   ├── api-gateway.yaml
│   └── kustomization.yaml
└── overlays/
    ├── dev/                 # 开发环境配置
    │   ├── kustomization.yaml
    │   ├── postgres-patch.yaml
    │   ├── redis-patch.yaml
    │   ├── minio-patch.yaml
    │   ├── content-service-patch.yaml
    │   └── replicas-patch.yaml
    └── prod/                # 生产环境配置
        ├── kustomization.yaml
        ├── replicas-patch.yaml
        ├── resources-patch.yaml
        └── api-gateway-service-patch.yaml
```

### 环境配置对比

| 配置项 | 开发环境 (dev) | 生产环境 (prod) |
|--------|---------------|----------------|
| **副本数** | 每个服务 1 个副本 | API Gateway: 3, 其他: 2 |
| **存储类型** | `emptyDir` (临时存储) | `PersistentVolumeClaim` |
| **存储大小** | 较小 (1Gi/512Mi/2Gi) | 较大 (5Gi/2Gi/10Gi) |
| **资源限制** | 较低 | 较高 |
| **GPU 支持** | 禁用 | 启用 (content-service) |
| **API Gateway** | ClusterIP | LoadBalancer (端口 80) |
| **镜像仓库** | 本地镜像 | 远程私有仓库 |

### 部署到开发环境

```bash
# 使用 k3s 部署开发环境
kubectl apply -k k8s/overlays/dev

# 查看状态
kubectl get pods -n ai-platform
kubectl get svc -n ai-platform

# 端口转发访问 (开发环境)
kubectl port-forward service/api-gateway 8000:8000 -n ai-platform
```

### 部署到生产环境

```bash
# 构建并推送镜像到私有仓库
docker build -f services/api-gateway/Dockerfile -t registry.example.com/ai-platform/api-gateway:latest .
docker push registry.example.com/ai-platform/api-gateway:latest

# 部署生产环境
kubectl apply -k k8s/overlays/prod

# 查看外部 IP
kubectl get service/api-gateway -n ai-platform -o wide
```

### K3s 轻量部署

```bash
# 安装 k3s (单节点)
curl -sfL https://get.k3s.io | sh -

# 查看节点
kubectl get nodes

# 部署应用
kubectl apply -k k8s/overlays/dev

# 检查状态
kubectl get pods -n ai-platform -w
```

### 环境变量配置

所有服务通过 ConfigMap 和 Secret 统一管理配置：

```yaml
# configmap (公开配置)
kubectl get configmap app-config -n ai-platform -o yaml

# secret (敏感配置 - base64 编码)
kubectl get secret app-secrets -n ai-platform -o yaml
```

---

## 🔄 CI/CD 流程

### 架构概览

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│   GitHub    │     │   Aliyun ACR    │     │   K3s/K8s   │
│   Actions   │────▶│   阿里云镜像仓库 │────▶│   集群部署   │
└─────────────┘     └─────────────────┘     └─────────────┘
```

### 分支策略

| 分支 | 触发行为 | 部署目标 |
|------|---------|---------|
| `develop` | 代码提交 | 开发环境 |
| `main` | 代码提交 | 仅构建推送 |
| `tags/v*` | 打标签 | 生产环境（需审批）|
| `pull_request` | PR 提交 | 仅测试 |

### 流水线阶段

```
代码提交 → Lint检查 → 构建镜像 → 运行测试 → 推送镜像 → 部署环境
```

#### Stage 1: Code Linting
- flake8: 代码风格检查
- black: 代码格式检查
- isort: 导入排序检查

#### Stage 2: Build
- 使用 Docker Buildx 构建
- 支持并行构建多个服务
- GitHub Actions 缓存优化

#### Stage 3: Test
- pytest 运行单元测试
- 异步测试支持

#### Stage 4: Push (仅 main/tags)
- 登录阿里云 ACR
- 推送镜像（带 SHA 标签和 latest）

#### Stage 5: Deploy
- **develop 分支**: 部署到开发环境
- **tags**: 部署到生产环境（需要审批）

### 阿里云镜像仓库配置

生产环境镜像地址：

| 服务 | 镜像地址 |
|------|---------|
| api-gateway | `registry.cn-hangzhou.aliyuncs.com/ai-platform-2026/api-gateway` |
| user-service | `registry.cn-hangzhou.aliyuncs.com/ai-platform-2026/user-service` |
| image-service | `registry.cn-hangzhou.aliyuncs.com/ai-platform-2026/image-service` |
| content-service | `registry.cn-hangzhou.aliyuncs.com/ai-platform-2026/content-service` |
| task-service | `registry.cn-hangzhou.aliyuncs.com/ai-platform-2026/task-service` |

### GitHub Secrets 配置

在 GitHub 仓库设置 -> Secrets and variables -> Actions 中添加以下 Secrets：

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `ALIYUN_REGISTRY_USERNAME` | 阿里云 ACR 用户名 | 阿里云控制台 |
| `ALIYUN_REGISTRY_PASSWORD` | 阿里云 ACR 密码 | 阿里云控制台 |
| `DEV_KUBECONFIG` | 开发环境 KubeConfig | `kubectl config view --raw \| base64` |
| `PROD_KUBECONFIG` | 生产环境 KubeConfig | `kubectl config view --raw \| base64` |

### 本地开发命令

#### 使用 Makefile (推荐)

```bash
# 构建所有镜像
make build

# 构建并推送到阿里云
make build-push IMAGE_TAG=v1.0.0

# 部署到开发环境
make deploy-dev

# 部署到生产环境
make deploy-prod

# 回滚部署
make rollback DEPLOYMENT=api-gateway

# 代码格式化
make format

# 运行测试
make test
```

#### 使用脚本

```bash
# 构建镜像
bash scripts/build.sh build

# 推送镜像
bash scripts/build.sh push

# 构建并推送
bash scripts/build.sh build-push

# 部署到开发环境
bash scripts/build.sh deploy-dev

# 部署到生产环境
bash scripts/build.sh deploy-prod

# 回滚
bash scripts/build.sh rollback api-gateway
```

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `REGISTRY` | registry.cn-hangzhou.aliyuncs.com | 镜像仓库地址 |
| `REPOSITORY` | ai-platform-2026 | 仓库命名空间 |
| `IMAGE_TAG` | latest | 镜像标签 |

### 回滚策略

```bash
# 查看部署历史
kubectl rollout history deployment/api-gateway -n ai-platform

# 回滚到上一版本
kubectl rollout undo deployment/api-gateway -n ai-platform

# 回滚到指定版本
kubectl rollout undo deployment/api-gateway -n ai-platform --to-revision=2
```

---

## 🏥 健康检查

启动后访问以下地址验证服务状态：

| 服务 | 健康检查地址 |
|-----|------------|
| **API Gateway** | http://localhost:18000/health |
| **User Service** | http://localhost:18001/health |
| **Image Service** | http://localhost:18002/health |
| **Content Service** | http://localhost:18003/health |
| **Task Service** | http://localhost:18004/health |
| **MinIO Console** | http://localhost:19001 |

> MinIO 登录凭据: `minioadmin` / `minioadmin`

---

## ⚠️ 注意事项

1. **构建上下文**: 确保从**项目根目录**运行 `docker build` 命令
2. **Docker 运行**: 确保 Docker Desktop 已启动并正常运行
3. **首次构建**: 首次构建可能需要较长时间下载 Python 依赖包
4. **端口占用**: 如果端口冲突，修改 `docker-compose.yml` 中的端口映射
5. **数据持久化**: 使用 `docker-compose down -v` 会删除所有数据，谨慎使用

---

## 🔧 故障排查

### 问题: 服务启动失败
```bash
# 查看具体服务日志
docker-compose logs <service-name>

# 例如: 查看 image-service 日志
docker-compose logs image-service
```

### 问题: 端口被占用
```bash
# 查看端口占用情况
lsof -i :<port>

# 修改 docker-compose.yml 中的端口映射
```

### 问题: 构建失败
```bash
# 清理缓存并重新构建
docker-compose build --no-cache <service-name>
```
