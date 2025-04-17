FROM python:3.9-slim

WORKDIR /app

# Install system dependencies with retry for better reliability
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsndfile1 \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements except torch
COPY requirements.txt .
RUN grep -v "torch" requirements.txt | grep -v "^#" > requirements-clean.txt && \
    pip install --no-cache-dir --timeout=7000 -r requirements-clean.txt

# Install seaborn which is missing
RUN pip install seaborn

# Download PyTorch with retry mechanism
RUN mkdir -p /tmp/torch && \
    cd /tmp/torch && \
    wget --timeout=7200 --tries=3 --retry-connrefused https://download.pytorch.org/whl/cpu/torch-1.10.0%2Bcpu-cp39-cp39-linux_x86_64.whl && \
    pip install /tmp/torch/torch-1.10.0+cpu-cp39-cp39-linux_x86_64.whl && \
    rm -rf /tmp/torch

# Copy the source code
COPY . .

# Create directories
RUN mkdir -p /app/data/recordings /app/data/db /app/reports

ENV PYTHONPATH=/app
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT -w 4 src.api.main:app"]