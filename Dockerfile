# -------- Builder --------
FROM python:3.11-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
COPY . .

RUN uv sync --no-dev


# -------- Runtime --------
FROM python:3.11-slim

WORKDIR /app

# Copy app + virtual environment
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in compose)
CMD ["local"]
