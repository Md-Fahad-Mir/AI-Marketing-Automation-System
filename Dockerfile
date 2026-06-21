# syntax=docker/dockerfile:1

###########################################################
# Stage 1 — builder: resolve & install deps with uv
###########################################################
FROM python:3.13-slim AS builder

# Bring in the uv binary (fast, reproducible installs from uv.lock).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Install dependencies only (no project, no dev deps) — cached unless the
# lockfile changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

###########################################################
# Stage 2 — runtime: slim image, no build tools
###########################################################
FROM python:3.13-slim AS runtime

LABEL org.opencontainers.image.title="AI Marketing Automation System" \
      org.opencontainers.image.description="FastAPI backend for AI-driven marketing campaign automation" \
      org.opencontainers.image.source="https://hub.docker.com/r/fahad1000mir/ai-marketing-automation"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    DATABASE_URL="sqlite:////app/data/marketing.db" \
    IMAGE_STORAGE_DIR="/app/data/generated_images"

WORKDIR /app

# Run as an unprivileged system user.
RUN groupadd --system app && useradd --system --gid app --no-create-home app

# Copy the prebuilt virtualenv (deps only) and the application code.
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app app ./app

# Writable data dir for the SQLite DB and generated images — mount a volume here.
RUN mkdir -p /app/data/generated_images && chown -R app:app /app/data

USER app
EXPOSE 8000

# IMPORTANT: a single worker is intentional. The app runs an in-process
# scheduler, so multiple workers would dispatch each campaign more than once.
# Scale horizontally only after externalizing the scheduler (see README).
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn_worker.UvicornWorker", \
     "--workers", "1", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
