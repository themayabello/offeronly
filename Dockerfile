FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
        portaudio19-dev \
        ffmpeg \
        libasound-dev \
        gcc \
        g++ \
        make \
        curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Render configuration
ENV PORT=10000
EXPOSE $PORT

HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]