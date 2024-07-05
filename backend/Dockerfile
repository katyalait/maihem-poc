# Start with a base image that includes Python
FROM python:3.11-slim

# Create a non-root user with UID 10001
RUN useradd -u 10001 myuser

# Switch to the root user for installing system dependencies
USER root

# Install system dependencies for tesseract and poppler-utils
RUN apt-get update && apt-get install  \
    ffmpeg libsm6 libxext6  \
    tesseract-ocr \
    poppler-utils \
    -y \
    && apt-get clean

# Create and set the working directory
WORKDIR /app

# Ensure the /app directory is owned by the non-root user
RUN chown -R myuser:myuser /app

# Switch to the non-root user
USER 10001

# Set environment variables to prevent Python from writing .pyc files and to not buffer output
ENV PYTHONUNBUFFERED=1

# Set environment variable for Poetry virtual environments path
ENV POETRY_VIRTUALENVS_PATH="/app/.venv"

# Copy only the necessary files first (to leverage Docker cache)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Set environment variables for Flask
ENV FLASK_APP=app.py

# Expose the port the app runs on
EXPOSE 5000

# Command to run the Flask app
CMD ["poetry", "run", "flask", "run", "--host", "0.0.0.0"]
