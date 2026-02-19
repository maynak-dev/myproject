# Use official Python slim image
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input

# Create a non-root user to run the app
RUN addgroup --system django && adduser --system --group django
USER django

# Expose port (adjust if your app uses a different port)
EXPOSE 8000

# Start gunicorn with multiple workers (recommended for production)
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]