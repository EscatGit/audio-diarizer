FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install ffmpeg and other system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload and results directories
RUN mkdir -p uploads results

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV DIARIZER_TYPE=lightweight

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
