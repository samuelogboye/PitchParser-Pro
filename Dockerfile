# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Create unprivileged user
RUN adduser --disabled-password --gecos '' app  

# Change ownership to the app user (optional)
RUN chown -R app:app /app

# Run as unprivileged user
USER app

# Set default command
CMD ["./scripts/run_celery.sh"]
