# ai-service/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
# ADDED: build-essential (This contains the C++ compiler required for dlib)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
# This will now compile dlib automatically because we added build-essential above
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create models directory
RUN mkdir -p /app/models /app/storage

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]