# File: deep-ml-fastai/Dockerfile
# Inherits from the shared GPU base image (PyTorch + CUDA)
FROM ml-lab-base-cuda123:latest

WORKDIR /tmp

COPY deep-ml-fastai/pyproject.toml deep-ml-fastai/uv.lock ./
RUN uv sync --frozen

WORKDIR /workspace

COPY shared/scripts/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=antigravity"]
