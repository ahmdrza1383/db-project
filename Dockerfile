# Use an official Python base image
FROM python:3.11-slim

LABEL org.opencontainers.image.authors="safar.com"


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /code  

# Copy only requirements first (for better caching)
COPY requirements.txt .  

# Install dependencies in one efficient step
RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install --no-cache-dir -r requirements.txt  

# Copy the rest of the application files
COPY . .  
