# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Install system dependencies (required for PyPDF2, pptx, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r celeryuser && useradd -r -g celeryuser celeryuser && chown -R celeryuser:celeryuser /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

USER celeryuser

# Environment variables (override in docker-compose.yml if needed)
ENV FLASK_APP=app/__init__.py
ENV FLASK_ENV=production

# Expose port (matches Flask's default)
EXPOSE 5000

# Command to run the app (Gunicorn for production)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]