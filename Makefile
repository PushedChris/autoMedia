.PHONY: build push build-push deploy-dev deploy-prod rollback lint test clean help

REGISTRY ?= registry.cn-hangzhou.aliyuncs.com
REPOSITORY ?= ai-platform-2026
IMAGE_TAG ?= latest
SHELL := /bin/bash

build:
	@echo "Building all Docker images..."
	@bash scripts/build.sh build

push:
	@echo "Pushing all Docker images..."
	@bash scripts/build.sh push

build-push:
	@echo "Building and pushing all Docker images..."
	@bash scripts/build.sh build-push

deploy-dev:
	@echo "Deploying to development environment..."
	@bash scripts/build.sh deploy-dev

deploy-prod:
	@echo "Deploying to production environment..."
	@bash scripts/build.sh deploy-prod

rollback:
	@if [ -z "$(DEPLOYMENT)" ]; then echo "Usage: make rollback DEPLOYMENT=<deployment-name>"; exit 1; fi
	@bash scripts/build.sh rollback $(DEPLOYMENT)

lint:
	@echo "Running code linting..."
	@flake8 services/ shared/ --max-line-length=120
	@black --check services/ shared/
	@isort --check services/ shared/

format:
	@echo "Formatting code..."
	@black services/ shared/
	@isort services/ shared/

test:
	@echo "Running tests..."
	@pytest tests/ -v --tb=short

clean:
	@echo "Cleaning up..."
	@docker system prune -f

help:
	@echo "Available commands:"
	@echo "  build          - Build all Docker images"
	@echo "  push           - Push all Docker images to registry"
	@echo "  build-push     - Build and push all Docker images"
	@echo "  deploy-dev     - Deploy to development environment"
	@echo "  deploy-prod    - Deploy to production environment"
	@echo "  rollback       - Rollback deployment (use DEPLOYMENT=<name>)"
	@echo "  lint           - Run code linting"
	@echo "  format         - Format code with black and isort"
	@echo "  test           - Run tests"
	@echo "  clean          - Clean up Docker resources"
	@echo "  help           - Show this help message"
	@echo ""
	@echo "Environment variables:"
	@echo "  REGISTRY       - Docker registry (default: registry.cn-hangzhou.aliyuncs.com)"
	@echo "  REPOSITORY     - Docker repository name (default: ai-platform-2026)"
	@echo "  IMAGE_TAG      - Docker image tag (default: latest)"
