FROM python:3.12-slim


WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

# Copy only necessary files for dependency installation
COPY pyproject.toml README.md* alembic.ini ./

RUN uv venv
RUN uv pip install -e .

# Application source code will be mounted via docker-compose

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]