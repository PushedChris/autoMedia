#!/bin/bash
# Secret 生成脚本

set -e

echo "==============================================="
echo "🔐 Kubernetes Secret 生成工具"
echo "==============================================="
echo ""

# 获取项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
SECRETS_FILE="$PROJECT_DIR/k8s/base/secrets.yaml"

# 读取当前 Secret 文件
echo "📋 当前配置文件: $SECRETS_FILE"
echo ""

# 获取用户输入
echo "请输入以下信息："
read -p "阿里云镜像仓库地址 [registry.cn-hangzhou.aliyuncs.com]: " REGISTRY_URL
REGISTRY_URL=${REGISTRY_URL:-registry.cn-hangzhou.aliyuncs.com}

read -p "阿里云镜像仓库用户名: " REGISTRY_USERNAME

read -sp "阿里云镜像仓库密码: " REGISTRY_PASSWORD
echo ""

read -p "阿里云镜像仓库命名空间 [ai-platform-2026]: " REGISTRY_NAMESPACE
REGISTRY_NAMESPACE=${REGISTRY_NAMESPACE:-ai-platform-2026}

read -p "MinIO 访问密钥 [minioadmin]: " MINIO_ACCESS_KEY
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}

read -sp "MinIO 秘密密钥 [minioadmin]: " MINIO_SECRET_KEY
MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
echo ""

read -p "数据库密码 [postgres]: " DATABASE_PASSWORD
DATABASE_PASSWORD=${DATABASE_PASSWORD:-postgres}

# 编码为 base64
encode() {
    if [[ "$1" != "" ]]; then
        echo -n "$1" | base64
    else
        echo ""
    fi
}

echo ""
echo "==============================================="
echo "📝 生成的 Secret 配置"
echo "==============================================="
cat > "$SECRETS_FILE" << EOF
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: ai-platform
type: Opaque
data:
  # MinIO 凭据
  MINIO_ACCESS_KEY: $(encode "$MINIO_ACCESS_KEY")
  MINIO_SECRET_KEY: $(encode "$MINIO_SECRET_KEY")
  
  # 数据库密码
  DATABASE_PASSWORD: $(encode "$DATABASE_PASSWORD")
  
  # 镜像仓库配置
  REGISTRY_URL: $(encode "$REGISTRY_URL")
  REGISTRY_USERNAME: $(encode "$REGISTRY_USERNAME")
  REGISTRY_PASSWORD: $(encode "$REGISTRY_PASSWORD")
  REGISTRY_NAMESPACE: $(encode "$REGISTRY_NAMESPACE")
EOF

echo ""
echo "✅ Secret 文件已更新！"
echo "📄 位置: $SECRETS_FILE"
echo ""
echo "🚀 下一步："
echo "1. 查看确认: cat $SECRETS_FILE"
echo "2. 部署: kubectl apply -k k8s/base"
echo ""
echo "==============================================="
