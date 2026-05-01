#!/bin/bash
set -e

REGISTRY=${REGISTRY:-registry.cn-hangzhou.aliyuncs.com}
REPOSITORY=${REPOSITORY:-ai-platform-2026}
IMAGE_TAG=${IMAGE_TAG:-latest}

SERVICES=(
  "api-gateway"
  "user-service"
  "image-service"
  "content-service"
  "task-service"
)

build() {
  echo "=== Building Docker images ==="
  for service in "${SERVICES[@]}"; do
    echo "Building $service..."
    docker build -f "services/$service/Dockerfile" -t "$REGISTRY/$REPOSITORY/$service:$IMAGE_TAG" .
  done
  echo "✅ All images built successfully!"
}

push() {
  echo "=== Logging into registry ==="
  docker login "$REGISTRY"

  echo "=== Pushing Docker images ==="
  for service in "${SERVICES[@]}"; do
    echo "Pushing $service..."
    docker push "$REGISTRY/$REPOSITORY/$service:$IMAGE_TAG"
    docker tag "$REGISTRY/$REPOSITORY/$service:$IMAGE_TAG" "$REGISTRY/$REPOSITORY/$service:latest"
    docker push "$REGISTRY/$REPOSITORY/$service:latest"
  done
  echo "✅ All images pushed successfully!"
}

build_and_push() {
  build
  push
}

deploy_dev() {
  echo "=== Deploying to Development ==="
  kubectl apply -k k8s/overlays/dev --record
  echo "✅ Deployed to development environment!"
}

deploy_prod() {
  echo "=== Deploying to Production ==="
  kubectl apply -k k8s/overlays/prod --record
  echo "✅ Deployed to production environment!"
}

rollback() {
  echo "=== Rolling back deployment ==="
  kubectl rollout undo deployment/$1 -n ai-platform
  echo "✅ Rollback completed!"
}

case "$1" in
  build)
    build
    ;;
  push)
    push
    ;;
  build-push)
    build_and_push
    ;;
  deploy-dev)
    deploy_dev
    ;;
  deploy-prod)
    deploy_prod
    ;;
  rollback)
    rollback "$2"
    ;;
  *)
    echo "Usage: $0 {build|push|build-push|deploy-dev|deploy-prod|rollback <deployment>}"
    exit 1
    ;;
esac
