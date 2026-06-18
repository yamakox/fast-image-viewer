FROM astral/uv:python3.13-alpine

WORKDIR "/app"
COPY "./backend/" "./"

RUN uv sync --no-dev

ENV STATIC_ROOT="/usr/share/nginx/html/static/"
RUN uv run manage.py collectstatic

CMD ["uv", "run", "main.py"]
