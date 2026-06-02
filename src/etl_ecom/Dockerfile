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

# IMPORTANT
ENV PYTHONPATH=/app

# Install poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock /app/

# Install dependencies
RUN poetry install --no-root

# Create required directories
RUN mkdir -p /app/warehouse

# Copy source code
COPY . .

# Start pipeline
CMD ["python", "-m", "etl_ecom.pipeline"]
