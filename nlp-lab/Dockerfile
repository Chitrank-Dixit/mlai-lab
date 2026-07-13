# File: nlp-lab/Dockerfile
# Inherits from the shared CPU base image
FROM ml-lab-base-cpu:latest

# Set up temporary working directory for build
WORKDIR /tmp

# Copy dependency configuration files
COPY nlp-lab/pyproject.toml nlp-lab/uv.lock ./

# Sync locked dependencies system-wide inside the container
RUN uv sync --frozen

# Pre-download spaCy English model and standard NLTK datasets
# Since spaCy is installed system-wide, we download directly
RUN python -m spacy download en_core_web_sm \
    && python -m nltk.downloader stopwords punkt

# Reset working directory to workspace
WORKDIR /workspace

# Copy wait-for-it script to ensure sync with MLflow
COPY shared/scripts/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Expose Jupyter port
EXPOSE 8888

# Default command to run JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=antigravity"]
