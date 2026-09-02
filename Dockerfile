FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV UV_PYTHON=3.13.15

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    gnupg \
    xvfb \
    xauth \
    python3-tk \
    fonts-noto-cjk \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2t64 \
    libgbm1 \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome 설치
RUN wget -q \
    https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    -O /tmp/google-chrome.deb \
    && apt-get update \
    && apt-get install -y /tmp/google-chrome.deb \
    && rm /tmp/google-chrome.deb \
    && rm -rf /var/lib/apt/lists/*

# uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN uv python install 3.13.15

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "python", "-u", "main.py"]