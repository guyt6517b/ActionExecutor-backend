# Use a slim Python image
FROM python:3.13-slim

# Install dependencies for Chrome + Selenium
RUN apt-get update && \
    apt-get install -y wget unzip chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

# Set environment variable for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="$PATH:/usr/bin/chromium"

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . .

# Expose port for Gunicorn
EXPOSE 8000

# Start the app using Gunicorn
CMD ["gunicorn", "wsgi:app", "-b", "0.0.0.0:8000"]
