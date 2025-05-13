FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc libpq-dev \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv for package management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml README.md* alembic.ini ./

# Create and activate virtual environment
RUN uv venv

# Install dependencies from pyproject.toml
RUN uv pip install -e "."

# Explicitly install required packages for migrations and data ingestion
RUN pip install python-dotenv pandas sqlalchemy psycopg2-binary requests beautifulsoup4 lxml alembic

# Install development dependencies if ARG INSTALL_DEV=true
ARG INSTALL_DEV=false
RUN if [ "${INSTALL_DEV}" = "true" ]; then \
    echo "Installing development dependencies..."; \
    uv pip install -e ".[dev]"; \
    else \
    echo "Skipping development dependencies."; \
    fi

# Copy application files
COPY ./app ./app
COPY ./migrations ./migrations
COPY ./tests ./tests

# Add the parent directory to Python path so the app package can be imported from anywhere
ENV PYTHONPATH=/app:$PYTHONPATH

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
