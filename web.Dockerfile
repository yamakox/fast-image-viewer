FROM node:lts-alpine AS builder

WORKDIR "/app"
COPY "./frontend/" "./"

ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm install
RUN npm run build

FROM astral/uv:python3.13-alpine AS backend-builder

WORKDIR "/app"
COPY "./backend/" "./"

RUN uv sync --no-dev

ENV STATIC_ROOT="/usr/share/nginx/html/static/"
RUN uv run --no-dev manage.py collectstatic

FROM nginx:stable-alpine-slim AS runner

COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=backend-builder /usr/share/nginx/html/static /usr/share/nginx/html/static
COPY ./nginx/conf.d/app.conf /etc/nginx/conf.d/app.conf
