# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.3

# Copy dependency files only first (Docker layer cache)
COPY pyproject.toml poetry.lock* ./

# Install deps without dev dependencies
RUN poetry config virtualenvs.in-project true \
    && poetry install --only main --no-root

    
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /app/.venv .venv

# Copy source code
COPY mcp_gateway/ ./mcp_gateway/
COPY adapters/    ./adapters/
COPY slack_bot/   ./slack_bot/

# Activate venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Non-root user — bonne pratique sécurité
RUN adduser --disabled-password --gecos "" appuser
USER appuser

CMD ["python", "-m", "slack_bot.bot"]