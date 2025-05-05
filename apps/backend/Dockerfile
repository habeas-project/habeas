FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc libpq-dev \
    # Add curl for healthcheck
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv package manager
RUN pip install uv

# Copy dependency definition files
COPY pyproject.toml README.md* alembic.ini ./

# Setup virtual environment
RUN uv venv
ENV VIRTUAL_ENV=/.venv
ENV PATH="/.venv/bin:$PATH"

# Install dependencies (use uv for faster installs)
ARG INSTALL_DEV=false
RUN uv pip install -e "."
RUN if [ "$INSTALL_DEV" = "true" ]; then \
    echo "Installing development dependencies..."; \
    uv pip install -e ".[dev]"; \
    else \
    echo "Skipping development dependencies."; \
    fi

# Copy the rest of the application code
COPY ./app ./app
COPY ./migrations ./migrations
COPY ./tests ./tests

# Default command to run the application using uvicorn via uv
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
