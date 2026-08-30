FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL -o /usr/local/bin/caddy \
        "https://github.com/caddyserver/caddy/releases/latest/download/caddy_linux_amd64" \
    && chmod +x /usr/local/bin/caddy \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /home/user/app

COPY --chown=user pyproject.toml README.md ./
COPY --chown=user src ./src
RUN pip install --user --no-cache-dir -e ".[all,api,mcp]"

COPY --chown=user app ./app
COPY --chown=user Caddyfile launcher.sh ./
RUN chmod +x launcher.sh

EXPOSE 7860
CMD ["./launcher.sh"]
