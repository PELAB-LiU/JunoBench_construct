# Complete JunoBench Dockerfile with ALL requirements
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    TORCH_CUDA_ARCH_LIST="" \
    FORCE_CUDA=0

# Install system dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    wget \
    curl \
    ca-certificates \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Copy requirements file
COPY data/requirements.txt requirements.txt

# Install ALL Python packages from requirements.txt (CPU-only for multi-platform)
RUN pip install --timeout 1000 --retries 3 -r requirements.txt

# Create directories for Jupyter
RUN mkdir -p /root/.jupyter

# Expose Jupyter port
EXPOSE 8888

# Default command (run as root with allow-root flag)
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]