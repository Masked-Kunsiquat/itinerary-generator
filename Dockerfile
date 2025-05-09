# Dockerfile for Phase 2: Web UI
FROM python:alpine

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    curl \
    build-base \
    libffi-dev \
    tzdata \
    ca-certificates

# Copy all project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Expose Flask's default port
EXPOSE 5000

# Run the web app
CMD ["python", "app.py"]
