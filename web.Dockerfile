FROM node:lts-alpine AS builder

WORKDIR "/app"
COPY "./frontend/" "./"

ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm install
RUN npm run build

FROM nginx:stable-alpine-slim AS runner

COPY --from=builder /app/dist /usr/share/nginx/html
COPY ./nginx/conf.d/app.conf /etc/nginx/conf.d/app.conf
