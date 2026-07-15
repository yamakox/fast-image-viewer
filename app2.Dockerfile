# backend2 (FastAPI) — multi-stage build
# Build: docker build -f app2.Dockerfile -t fast-image-viewer-app2 .

FROM astral/uv:python3.13-alpine AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
# Git 無しのビルドでも poetry-dynamic-versioning を通す
ENV POETRY_DYNAMIC_VERSIONING_BYPASS=0.0.0

# 依存だけ先に入れてレイヤーキャッシュを効かせる
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend2/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend2/pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=backend2/README.md,target=README.md \
    uv sync --locked --no-install-project --no-editable

COPY ./backend2/ /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.13-alpine AS runner

WORKDIR /app

# ソースは載せない。.venv（非 editable インストール済み）と起動・migrate 用のみ
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/main.py /app/main.py
COPY --from=builder /app/alembic.ini /app/alembic.ini
COPY --from=builder /app/alembic /app/alembic

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "main.py"]
