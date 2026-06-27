#!/bin/bash
set -e

echo "Starting Bare Metal setup for AI Influencer Studio on RunPod..."

# Update and install Redis
apt-get update
apt-get install -y redis-server git
service redis-server start

# Create directories
mkdir -p data/models/unet
mkdir -p data/models/loras
mkdir -p data/models/vae
mkdir -p data/models/clip
mkdir -p data/datasets
mkdir -p data/workflows
mkdir -p data/calendar

# Install Backend Requirements
python3 -m pip install -r backend/requirements.txt

# Start Celery Worker in background
cd backend
nohup celery -A celery_app worker --loglevel=info > ../data/celery.log 2>&1 &
cd ..

# Start FastAPI Backend in background
cd backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../data/api.log 2>&1 &
cd ..

echo "Services started! API is running on port 8000."
echo "Check data/api.log and data/celery.log for output."

# Clone and setup ComfyUI if it doesn't exist
if [ ! -d "data/ComfyUI" ]; then
    echo "Downloading ComfyUI..."
    cd data
    git clone https://github.com/comfyanonymous/ComfyUI.git
    cd ComfyUI
    pip install -r requirements.txt
    cd ../..
fi

# Start ComfyUI
echo "Starting ComfyUI on port 8188..."
cd data/ComfyUI
nohup python main.py --listen 0.0.0.0 > ../comfyui.log 2>&1 &
cd ../..

echo "All services successfully started on Bare Metal!"
