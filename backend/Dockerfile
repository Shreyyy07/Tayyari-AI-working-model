FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required for audio processing (Whisper)
RUN apt-get update && apt-get install -y \
    ffmpeg git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install setuptools first (fixes the pkg_resources error for openai-whisper)
RUN pip install --no-cache-dir setuptools wheel

# Install the rest of the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories for the app
RUN mkdir -p uploads downloads

# Copy the rest of the application code
COPY . .

# Hugging Face Spaces expects apps to run on port 7860 by default
EXPOSE 7860

# Command to run the Flask application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]
