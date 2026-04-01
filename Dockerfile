FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment setup
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV CAMERA_SOURCE=0

EXPOSE 5000

CMD ["flask", "run"]
