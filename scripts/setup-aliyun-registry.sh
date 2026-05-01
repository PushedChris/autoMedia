#!/bin/bash
# 阿里云镜像仓库配置脚本

set -e

echo "==============================================="
echo "☁️  阿里云镜像仓库配置工具"
echo "==============================================="
echo ""

# 获取项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# 获取用户输入
echo "请输入阿里云镜像仓库信息："
read -p "阿里云镜像仓库地址 [registry.cn-hangzhou.aliyuncs.com]: " REGISTRY_URL
REGISTRY_URL=${REGISTRY_URL:-registry.cn-hangzhou.aliyuncs.com}

read -p "镜像仓库命名空间 [ai-platform-2026]: " REGISTRY_NAMESPACE
REGISTRY_NAMESPACE=${REGISTRY_NAMESPACE:-ai-platform-2026}

read -p "镜像标签 [latest]: " IMAGE_TAG
IMAGE_TAG=${IMAGE_TAG:-latest}

echo ""
echo "==============================================="
echo "📝 更新配置文件"
echo "==============================================="

# 更新生产环境 kustomization.yaml
KUSTOMIZE_FILE="$PROJECT_DIR/k8s/overlays/prod/kustomization.yaml"

cat > "$KUSTOMIZE_FILE" << EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

patches:
  - path: replicas-patch.yaml
  - path: resources-patch.yaml
  - path: api-gateway-service-patch.yaml

images:
  - name: api-gateway
    newName: ${REGISTRY_URL}/${REGISTRY_NAMESPACE}/api-gateway
    newTag: ${IMAGE_TAG}
  - name: user-service
    newName: ${REGISTRY_URL}/${REGISTRY_NAMESPACE}/user-service
    newTag: ${IMAGE_TAG}
  - name: image-service
    newName: ${REGISTRY_URL}/${REGISTRY_NAMESPACE}/image-service
    newTag: ${IMAGE_TAG}
  - name: content-service
    newName: ${REGISTRY_URL}/${REGISTRY_NAMESPACE}/content-service
    newTag: ${IMAGE_TAG}
  - name: task-service
    newName: ${REGISTRY_URL}/${REGISTRY_NAMESPACE}/task-service
    newTag: ${IMAGE_TAG}
EOF

# 更新 Makefile
MAKEFILE="$PROJECT_DIR/Makefile"
if [ -f "$MAKEFILE" ]; then
    sed -i '' "s|REGISTRY ?=.*|REGISTRY ?= ${REGISTRY_URL}|" "$MAKEFILE"
    sed -i '' "s|REPOSITORY ?=.*|REPOSITORY ?= ${REGISTRY_NAMESPACE}|" "$MAKEFILE"
fi

# 更新 build.sh
BUILD_SCRIPT="$PROJECT_DIR/scripts/build.sh"
if [ -f "$BUILD_SCRIPT" ]; then
    sed -i '' "s|REGISTRY=.*|REGISTRY=${REGISTRY_URL}|" "$BUILD_SCRIPT"
    sed -i '' "s|REPOSITORY=.*|REPOSITORY=${REGISTRY_NAMESPACE}|" "$BUILD_SCRIPT"
fi

echo ""
echo "✅ 配置文件已更新！"
echo "📄 位置: $KUSTOMIZE_FILE"
echo ""
echo "🚀 下一步："
echo "1. 确认配置: cat $KUSTOMIZE_FILE"
echo "2. 生成镜像并推送: make build-push IMAGE_TAG=$IMAGE_TAG"
echo "3. 部署: kubectl apply -k k8s/overlays/prod"
echo ""
echo "==============================================="
