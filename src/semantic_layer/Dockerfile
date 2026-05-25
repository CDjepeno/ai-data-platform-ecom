FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    # Clean apt cache in the same layer to avoid bloat
    && apt-get clean

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1

# HuggingFace will cache models here at runtime — mounted as a volume in K8s
ENV HF_HOME=/mnt/hf-cache

RUN pip install --upgrade pip && pip install poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

# No model download here — image stays lightweight
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]