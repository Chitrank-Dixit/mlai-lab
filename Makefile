# File: Makefile
# Helper file to easily manage environments, build images, and run specific labs

.PHONY: help init build-base build-base-cpu build-base-cuda build-all basic deep fastai nlp cv rl down clean

DOCKER_NATIVE := $(shell docker --version >/dev/null 2>&1 && echo "docker")
DOCKER_EXE := $(shell docker.exe --version >/dev/null 2>&1 && echo "docker.exe")
DOCKER ?= $(if $(DOCKER_NATIVE),$(DOCKER_NATIVE),$(if $(DOCKER_EXE),$(DOCKER_EXE),docker))

# Default rule: show help
help:
	@echo "========================================================================"
	@echo "AI/ML Monorepo Lab Control"
	@echo "========================================================================"
	@echo "Management Commands:"
	@echo "  make init             - Copy .env.example to .env and setup shared network/volumes"
	@echo "  make build-base       - Build CPU and CUDA base images"
	@echo "  make build-base-cpu   - Build CPU base image only"
	@echo "  make build-base-cuda  - Build CUDA base image only"
	@echo "  make down             - Spin down all running services"
	@echo "  make clean            - Spin down services and delete named volumes/data"
	@echo ""
	@echo "Run Specific Labs (spins up MLflow automatically):"
	@echo "  make basic            - Build and launch Basic ML Lab (Port 8888)"
	@echo "  make deep             - Build and launch Deep ML Lab (Port 8889) (GPU)"
	@echo "  make fastai           - Build and launch fast.ai Lab (Port 8893) (GPU)"
	@echo "  make nlp              - Build and launch NLP Lab (Port 8890)"
	@echo "  make cv               - Build and launch CV Lab (Port 8891) (GPU)"
	@echo "  make rl               - Build and launch RL Lab (Port 8892) (GPU)"
	@echo "========================================================================"

init:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
	else \
		echo ".env already exists"; \
	fi
	$(DOCKER) network create ml-lab-net 2>/dev/null || true
	$(DOCKER) volume create shared_notebooks 2>/dev/null || true

build-base-cpu:
	$(DOCKER) build -t ml-lab-base-cpu:latest -f base/Dockerfile.cpu .

build-base-cuda:
	$(DOCKER) build -t ml-lab-base-cuda123:latest -f base/Dockerfile.cuda123 .

build-base: build-base-cpu build-base-cuda

basic: init build-base-cpu
	$(DOCKER) compose -f compose.shared.yml -f compose.basic-ml.yml up -d --build
	@echo "Basic ML Lab starting at http://localhost:8888 (MLflow tracker: http://localhost:5000)"

deep: init build-base-cuda
	$(DOCKER) compose -f compose.shared.yml -f compose.deep-ml.yml up -d --build
	@echo "Deep ML Lab starting at http://localhost:8889 (MLflow tracker: http://localhost:5000)"

fastai: init build-base-cuda
	$(DOCKER) compose -f compose.shared.yml -f compose.fastai.yml up -d --build
	@echo "fast.ai Lab starting at http://localhost:8893 (MLflow tracker: http://localhost:5000)"

nlp: init build-base-cpu
	$(DOCKER) compose -f compose.shared.yml -f compose.nlp.yml up -d --build
	@echo "NLP Lab starting at http://localhost:8890 (MLflow tracker: http://localhost:5000)"

cv: init build-base-cuda
	$(DOCKER) compose -f compose.shared.yml -f compose.cv.yml up -d --build
	@echo "CV Lab starting at http://localhost:8891 (MLflow tracker: http://localhost:5000)"

rl: init build-base-cuda
	$(DOCKER) compose -f compose.shared.yml -f compose.rl.yml up -d --build
	@echo "RL Lab starting at http://localhost:8892 (MLflow tracker: http://localhost:5000)"

down:
	$(DOCKER) compose -f compose.shared.yml -f compose.basic-ml.yml -f compose.deep-ml.yml -f compose.fastai.yml -f compose.nlp.yml -f compose.cv.yml -f compose.rl.yml down

clean:
	$(DOCKER) compose -f compose.shared.yml -f compose.basic-ml.yml -f compose.deep-ml.yml -f compose.fastai.yml -f compose.nlp.yml -f compose.cv.yml -f compose.rl.yml down -v
