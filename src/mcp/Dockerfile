# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.3

# Copy dependency files first — Docker layer cache
# If pyproject.toml doesn't change, deps are not reinstalled
COPY pyproject.toml poetry.lock* ./

# Install runtime deps only — no dev deps in production image
RUN poetry config virtualenvs.in-project true \
    && poetry install --only main --no-root

# ── Runtime stage ──────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy virtualenv from builder — lean image, no Poetry needed
COPY --from=builder /app/.venv .venv

# Copy source code — new Clean Architecture structure
COPY domain/          ./domain/
COPY application/     ./application/
COPY infrastructure/  ./infrastructure/
COPY utils/           ./utils/
COPY py.typed         ./py.typed

# Activate virtualenv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Non-root user — security best practice
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Default: start MCP server
# Override with: docker run ... python -m infrastructure.slack.bot
# CMD ["python", "-m", "infrastructure.mcp.server"]
CMD ["python", "-m", "infrastructure.adapters.slack.bot"]