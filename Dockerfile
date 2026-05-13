FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python / Poetry env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1

# Install poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Copy dependency files first
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root

# Copy ONLY needed folders
COPY src/ ./src/


CMD ["python", "-m", "etl_ecommerce"]