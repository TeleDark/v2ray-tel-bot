FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt update && apt install -y libzbar0 cron

# Upgrade pip, wheel, and setuptools
RUN pip install -U pip wheel setuptools

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Setup cron jobs
RUN (echo "*/3 * * * * python3 /app/login.py"; echo "42 2 */2 * * rm -rf /app/cookies.pkl") | crontab -