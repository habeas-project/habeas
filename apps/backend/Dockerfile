FROM python:3.12-slim

WORKDIR /app

# Build argument to control dev dependency installation
ARG INSTALL_DEV=false

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install uv

COPY pyproject.toml README.md* alembic.ini ./

# Install dependencies
RUN uv venv
RUN uv pip install -e "."
RUN if [ "$INSTALL_DEV" = "true" ]; then \
    echo "Installing development dependencies..."; \
    uv pip install -e ".[dev]"; \
    fi

# Copy application source code
COPY ./app ./app
COPY ./migrations ./migrations
COPY ./tests ./tests



EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
