FROM ghcr.io/astral-sh/uv:python3.14-trixie AS builder

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY alembic.ini ./
COPY src/ ./src

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "src.main"]