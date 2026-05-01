#!/usr/bin/env bash
set -euo pipefail

export MINIO_ENDPOINT=${MINIO_ENDPOINT:-localhost:9000}
export MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
export MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
export BUCKETS=${MINIO_BUCKETS:-raw processed output}

if ! command -v mc >/dev/null 2>&1; then
  echo "请先安装 MinIO 客户端 mc。"
  exit 1
fi

mc alias set local http://${MINIO_ENDPOINT} ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}
for bucket in ${BUCKETS}; do
  if mc ls local/${bucket} >/dev/null 2>&1; then
    echo "Bucket ${bucket} 已存在。"
  else
    echo "创建 Bucket: ${bucket}"
    mc mb local/${bucket}
  fi
done

echo "MinIO Bucket 初始化完成。"
