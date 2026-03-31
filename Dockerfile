# ─────────────────────────────────────────────────────────────────────────────
# Dockerfile — MLOps Data Pipeline
# ─────────────────────────────────────────────────────────────────────────────
# Multi-stage build:
#   Stage 1 (base)  : Python + system deps + pip packages
#   Stage 2 (app)   : Copy source code, set entrypoint
#
# Build:
#   docker build -t mlops-pipeline .
#
# Run:
#   docker run --rm -v $(pwd)/data:/app/data mlops-pipeline
#   docker run --rm -v $(pwd)/data:/app/data mlops-pipeline --stages merge_daily
#   docker run --rm -v $(pwd)/data:/app/data mlops-pipeline --list
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Base image with dependencies ─────────────────────────────────────
FROM python:3.11-slim AS base

# System deps for git (needed by ingest_calendar.py and DVC)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (cached layer — only rebuilds when requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Application ──────────────────────────────────────────────────────
FROM base AS app

# Copy pipeline config
COPY params.yaml .
COPY dvc.yaml .
COPY pipeline.py .

# Copy source code
COPY src/ src/

# Copy calendar data (git-tracked, needed for prepare_calendar)
COPY data/calendar-events/ data/calendar-events/

# Copy data documentation
COPY data/WEATHER_DATA_README.md data/WEATHER_DATA_README.md
COPY data/CALENDAR_FEATURES_README.md data/CALENDAR_FEATURES_README.md

# Data directory is a mount point — pipeline writes here
VOLUME /app/data

# Health check: verify Python and key imports work
RUN python -c "import pandas, yaml; print('Dependencies OK')"

# Default entrypoint: the master pipeline script
ENTRYPOINT ["python", "pipeline.py"]

# Default command: full pipeline with verbose output
CMD ["-v"]
