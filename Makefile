# File: Makefile
# Helper file to easily manage environments, build images, and run specific labs

.PHONY: help init build-base build-base-cpu build-base-cuda build-all basic deep nlp cv rl down clean

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
	docker network create ml-lab-net 2>/dev/null || true
	docker volume create shared_notebooks 2>/dev/null || true

build-base-cpu:
	docker build -t ml-lab-base-cpu:latest -f base/Dockerfile.cpu .

build-base-cuda:
	docker build -t ml-lab-base-cuda123:latest -f base/Dockerfile.cuda123 .

build-base: build-base-cpu build-base-cuda

basic: init build-base-cpu
	docker compose -f compose.shared.yml -f compose.basic-ml.yml up -d --build
	@echo "Basic ML Lab starting at http://localhost:8888 (MLflow tracker: http://localhost:5000)"

deep: init build-base-cuda
	docker compose -f compose.shared.yml -f compose.deep-ml.yml up -d --build
	@echo "Deep ML Lab starting at http://localhost:8889 (MLflow tracker: http://localhost:5000)"

nlp: init build-base-cpu
	docker compose -f compose.shared.yml -f compose.nlp.yml up -d --build
	@echo "NLP Lab starting at http://localhost:8890 (MLflow tracker: http://localhost:5000)"

cv: init build-base-cuda
	docker compose -f compose.shared.yml -f compose.cv.yml up -d --build
	@echo "CV Lab starting at http://localhost:8891 (MLflow tracker: http://localhost:5000)"

rl: init build-base-cuda
	docker compose -f compose.shared.yml -f compose.rl.yml up -d --build
	@echo "RL Lab starting at http://localhost:8892 (MLflow tracker: http://localhost:5000)"

down:
	docker compose -f compose.shared.yml -f compose.basic-ml.yml -f compose.deep-ml.yml -f compose.nlp.yml -f compose.cv.yml -f compose.rl.yml down

clean:
	docker compose -f compose.shared.yml -f compose.basic-ml.yml -f compose.deep-ml.yml -f compose.nlp.yml -f compose.cv.yml -f compose.rl.yml down -v
