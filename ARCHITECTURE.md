# k3s + 本地 GPU + 云调度 + OSS 的商用部署架构

## 1. 目标概述

本方案面向AI图片创作平台，目标实现：
- 本地 GPU 推理优先，降低成本并减少延迟
- 云端弹性调度，支持高并发与批量任务
- 自建 OSS（MinIO）作为统一对象存储
- k3s 作为集群管理与调度基础
- 全链路可观测、可扩展、可运维

## 2. 核心组件

### 2.1 接入层
- Web 前端 / FastAPI
- API Gateway / Ingress
- 统一鉴权、限流、流量路由

### 2.2 业务层
- 用户服务
- 图片处理服务
- 内容生成服务
- 任务调度服务

### 2.3 AI 服务层
- LangChain Agent 调度引擎
- 多模型路由：本地 GPU / 云端高精度
- 图片理解、文案生成、风格优化

### 2.4 存储层
- MinIO 自建对象存储（OSS）
- PostgreSQL 业务数据
- Redis 缓存与队列

## 3. 部署架构

```
用户 → Web 前端 → API Gateway → k3s 集群
                          ↓
                 本地 GPU 推理集群
                          ↕
                 云端调度/批量集群
                          ↓
                   MinIO + PostgreSQL + Redis
```

### 3.1 本地边缘节点
- k3s 单节点或小规模多节点集群
- 本地 GPU 节点标记 `gpu=true`
- 本地 MinIO 用于低延迟对象存储
- 本地优先执行图片理解与实时生成任务

### 3.2 云端调度节点
- k3s 多节点云端集群
- 弹性扩容 CPU/GPU 资源
- 处理高并发、批量生成、云端补算
- 可接入云端 MinIO 或 S3 兼容 OSS

### 3.3 混合调度策略
- 优先本地推理
- 本地资源不足时转入云端
- 任务类型区分：实时任务 vs 批量任务
- 借助 `nodeAffinity`、`tolerations` 与业务调度组件

## 4. MinIO OSS 设计

### 4.1 Bucket 规划
- `raw`：原图上传
- `processed`：分析结果、中间文件
- `output`：最终生成图片/视频
- `models`：模型文件与权重缓存

### 4.2 同步与备份
- 本地 MinIO 与云端 MinIO 之间使用 Replication
- 数据备份策略：日增量、周全量、跨区域
- 最小权限策略与加密传输

## 5. 运维与安全

### 5.1 高可用
- 本地 k3s HA（可选）
- MinIO 分布式部署
- 云端 k3s 自动扩缩

### 5.2 监控与日志
- Prometheus + Grafana
- Loki / ELK 日志聚合
- 告警：GPU 利用率、任务积压、存储容量

### 5.3 安全
- API Gateway 鉴权与 TLS
- NetworkPolicy 限制服务访问
- 最小权限访问 MinIO 与数据库
- 证书管理：cert-manager

## 6. 交付清单

- `app/`：FastAPI 服务代码
- `k8s/`：k3s 部署清单
- `docker-compose.yml`：本地验证环境
- `scripts/setup_minio_buckets.sh`：MinIO Bucket 初始化
- `ARCHITECTURE.md`：架构说明文档

## 7. 推荐落地步骤

1. 本地验证：`docker-compose up`
2. 部署本地 k3s：`kubectl apply -f k8s/`
3. 配置 MinIO replication
4. 上线云端调度集群
5. 加入 Prometheus/Grafana 和告警
