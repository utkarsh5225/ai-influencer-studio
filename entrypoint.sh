#!/bin/bash
set -e

echo "Starting AI Influencer Studio on RunPod..."

# Ensure data directories exist
mkdir -p data/models/unet
mkdir -p data/models/loras
mkdir -p data/models/vae
mkdir -p data/models/clip
mkdir -p data/datasets
mkdir -p data/workflows
mkdir -p data/calendar

# Start docker-compose
docker-compose up -d

echo "Services started. Waiting for ComfyUI and API to be ready..."
sleep 10

echo "Studio is ready!"
echo "Backend API: http://localhost:8000"
echo "ComfyUI: http://localhost:8188"
