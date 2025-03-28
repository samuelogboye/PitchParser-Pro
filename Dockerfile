# Use official Python image
FROM python:3.9-slim

# # Install system dependencies (required for PyPDF2, pptx, etc.)
# RUN apt-get update && apt-get install -y \
#     gcc \
#     python3-dev \
#     && rm -rf /var/lib/apt/lists/*

# add requirements.txt to the image
ADD requirements.txt /app/requirements.txt

# # Create user and group first
# RUN groupadd -g 1001 celeryuser && \
#     useradd -u 1001 -g celeryuser celeryuser && \
#     mkdir -p /app/logs && \
#     chown -R celeryuser:celeryuser /app

# Set working directory
WORKDIR /app

# # Create logs directory with proper ownership
# RUN mkdir -p /app/logs && \
#     chown celeryuser:celeryuser /app/logs && \
#     chmod 755 /app/logs

# # Copy requirements and install Python packages
# COPY --chown=celeryuser:celeryuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code with proper ownership
# COPY --chown=celeryuser:celeryuser . .

# USER celeryuser

# # Expose port (matches Flask's default)
# EXPOSE 5000

# # Command to run the app (Gunicorn for production)
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
# create unprivileged user
RUN adduser --disabled-password --gecos '' app  