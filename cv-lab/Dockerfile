# File: cv-lab/Dockerfile
# Inherits from the shared CUDA base image
FROM ml-lab-base-cuda123:latest

# Install extra system libraries required by OpenCV and graphics rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set up temporary working directory for build
WORKDIR /tmp

# Copy dependency configuration files
COPY cv-lab/pyproject.toml cv-lab/uv.lock ./

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
