FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies
COPY backend/pyproject.toml ./backend/
COPY backend/app ./backend/app

# Install dependencies including crawler optional dependencies
RUN pip install --upgrade pip && \
    pip install "./backend[crawler]"

# Install playwright system dependencies and Chromium browser
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy crawler package
COPY crawler ./crawler

WORKDIR /app/crawler

# Default command: run Celery worker with single concurrency for low-resource environments
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info", "--concurrency=1"]
