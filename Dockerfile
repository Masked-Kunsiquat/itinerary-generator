# Dockerfile for Phase 2: Web UI
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy all project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Expose Flask's default port
EXPOSE 5000

# Run the web app
CMD ["python", "app.py"]
