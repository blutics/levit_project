FROM python:3.13.15-slim

# OS dependencies
#RUN apt-get update \
#    && apt-get install -y --no-install-recommends \
#        chromium \
#        xauth \
#        xvfb \
#        fonts-noto-cjk \
#        libnss3 \
#        libgtk-3-0 \
#        libgbm1 \
#    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    xvfb \
    xauth \
    python3-tk \
    fonts-noto-cjk \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libgbm1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev
COPY . .
CMD ["uv", "run", "python", "main.py"]