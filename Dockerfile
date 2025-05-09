FROM python:alpine

# Metadata labels
LABEL org.opencontainers.image.title="Surmai Itinerary Generator" \
      org.opencontainers.image.description="Web app for rendering Surmai trip exports to print-friendly templates" \
      org.opencontainers.image.version="1.0.1" \
      org.opencontainers.image.source="https://github.com/Masked-Kunsiquat/itinerary-generator" \
      org.opencontainers.image.licenses="MIT"

# Set working directory
WORKDIR /app

# Install system dependencies and add non-root user
RUN apk add --no-cache \
    curl \
    build-base \
    libffi-dev \
    tzdata \
    ca-certificates \
    shadow \
 && adduser -D -u 1000 appuser

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Fix permissions for non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Flask's default port
EXPOSE 5000

# Default command
CMD ["python", "-m", "itinerary_generator.web"]