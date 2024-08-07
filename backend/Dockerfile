# Start with a base image that includes Python
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files and to not buffer output
ENV PYTHONUNBUFFERED=1

# Install system dependencies for tesseract and poppler-utils
RUN apt-get update && apt-get install  \
    ffmpeg libsm6 libxext6  \
    tesseract-ocr \
    poppler-utils \
    -y \
    && apt-get clean

# Install Poetry
RUN pip install poetry

# Create and set the working directory
WORKDIR /app

# Copy only the necessary files first (to leverage Docker cache)
COPY pyproject.toml poetry.lock /app/

# Install Python dependencies
RUN poetry install --no-root

# Copy the rest of the application code
COPY . /app

# Set environment variables for Flask
ENV FLASK_APP=app.py

# Expose the port the app runs on
EXPOSE 5000

WORKDIR /app

# Command to run the Flask app
CMD ["poetry", "run", "flask", "run", "--host", "0.0.0.0"]