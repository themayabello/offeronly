# Use an official Python image
FROM python:3.11-slim
# Install system dependencies needed for PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    ffmpeg \
    libasound-dev \
    && rm -rf /var/lib/apt/lists/*
# Set the working directory
WORKDIR /app
# Copy everything into the container
COPY . .
# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt
# Expose the port used by uvicorn
EXPOSE 10000
# Run the FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]


