# File: deep-ml/Dockerfile
# Inherits from the shared CUDA base image
FROM ml-lab-base-cuda123:latest

# Set up temporary working directory for build
WORKDIR /tmp

# Copy dependency configuration files
COPY deep-ml/pyproject.toml deep-ml/uv.lock ./

# Sync locked dependencies system-wide inside the container
RUN uv sync --frozen

# Reset working directory to workspace
WORKDIR /workspace

# Copy wait-for-it script to ensure sync with MLflow
COPY shared/scripts/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Expose Jupyter port
EXPOSE 8888

# Default command to run JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=antigravity"]
