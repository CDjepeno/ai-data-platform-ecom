FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1

RUN pip install --upgrade pip && pip install poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

# 2. Then download the model (sentence_transformers is now installed)
ARG HF_TOKEN
RUN HUGGING_FACE_HUB_TOKEN=${HF_TOKEN} python -c \
    "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# 3. Finally copy the application code
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]