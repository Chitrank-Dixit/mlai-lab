# File: rl-lab/Dockerfile
# Inherits from the shared CPU base image
FROM ml-lab-base-cpu:latest

# Install system dependencies for OpenGL rendering, virtual framebuffers, and video logging
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    freeglut3-dev \
    libosmesa6-dev \
    patchelf \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set up temporary working directory for build
WORKDIR /tmp

# Copy dependency configuration files
COPY rl-lab/pyproject.toml rl-lab/uv.lock ./

# Sync dependencies system-wide inside the container
RUN uv sync

# Reset working directory to workspace
WORKDIR /workspace

# Copy wait-for-it script to ensure sync with MLflow
COPY shared/scripts/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Expose Jupyter port
EXPOSE 8888

# Default command to run JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=antigravity"]
