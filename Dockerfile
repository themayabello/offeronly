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

# Copy only backend contents
COPY backend/ .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Tell Render which port to scan
ENV PORT=10000

# Expose that port
EXPOSE 10000

# Run FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]



