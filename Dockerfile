FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    URL_PREFIX= \
    HOST=0.0.0.0 \
    PORT=8000 \
    WEB_CONCURRENCY=2 \
    PAGE_CACHE_SIZE=512 \
    AUDIO_CACHE_SIZE=500

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libharfbuzz-dev \
    libfreetype6-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "scripts/run_server.py", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
