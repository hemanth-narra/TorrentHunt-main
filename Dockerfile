FROM python:3.12-slim

# Install uv for ultra-fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create persistent data directory for telegram session and sqlite database
RUN mkdir -p /app/data

# Copy project definition and install dependencies
COPY pyproject.toml .
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application source code
COPY app app

# Environment settings: workdir points to mounted volume so session and database persist
ENV WORKDIR=/app/data
ENV PYTHONUNBUFFERED=1

VOLUME ["/app/data"]

CMD ["python", "app/main.py"]
