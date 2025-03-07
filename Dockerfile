FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Python requirements file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/uploads \
    /app/results \
    /app/app/templates \
    /app/app/static/css \
    /app/app/static/js \
    /app/app/api \
    /app/app/core

# Copy application files
COPY app/main.py /app/app/
COPY app/api/ /app/app/api/
COPY app/core/ /app/app/core/
COPY app/templates/ /app/app/templates/
COPY app/static/ /app/app/static/

# Create placeholder files if they don't exist
RUN if [ ! -f /app/app/templates/index.html ]; then \
    echo '<!DOCTYPE html><html><head><title>Audio Diarizer</title><link rel="stylesheet" href="/static/css/styles.css"></head><body><h1>Audio Diarizer</h1><p>Bienvenido al servicio de diarización de audio.</p><script src="/static/js/main.js"></script></body></html>' > /app/app/templates/index.html; \
    fi

RUN if [ ! -f /app/app/static/css/styles.css ]; then \
    echo 'body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }' > /app/app/static/css/styles.css; \
    fi

RUN if [ ! -f /app/app/static/js/main.js ]; then \
    echo 'console.log("Audio Diarizer loaded");' > /app/app/static/js/main.js; \
    fi

# Set environment variables
ENV PYTHONPATH=/app
ENV TEMPLATES_DIR=/app/app/templates
ENV STATIC_DIR=/app/app/static
ENV DIARIZER_TYPE=lightweight

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]