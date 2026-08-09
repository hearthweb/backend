ARG PYTHON_VERSION=3.14
ARG UV_VERSION=0.12.3


FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv


FROM python:${PYTHON_VERSION}-slim AS builder

# Install uv
COPY --from=uv /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Set Python and uv configuration
ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy

# Install project dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev --no-install-project --extra postgres

# Copy the source files
COPY . .

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --extra postgres


FROM python:${PYTHON_VERSION}-slim

# Set the working directory
WORKDIR /app

# Create a user and group for running the application
RUN groupadd -r app && \
    useradd -rg app app

# Copy the files from the builder
COPY --from=builder --chown=app:app /app /app

# Set a few important environment variables
ENV UPLOAD_DIR=/data \
    ENVIRONMENT=prod \
    PATH="/app/.venv/bin:$PATH"

# Specify the user
USER app

# Specify the volume for uploads
VOLUME /data

# Specify the command to run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
