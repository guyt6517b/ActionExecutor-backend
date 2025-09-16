# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for Chromium and other utilities
RUN apt-get update && \
    apt-get install -y chromium wget curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for Chromium
ENV CHROMIUM_BIN=/usr/bin/chromium
ENV CHROMIUM_PATH=/usr/lib/chromium

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000"]
