# AI Influencer Studio

A complete, production-ready AI Influencer Studio designed for **RunPod**.

## Architecture
- **Frontend**: React + Vite + Tailwind CSS (Runs locally or remote)
- **Backend**: FastAPI + Celery + Redis + PostgreSQL (Runs on RunPod)
- **AI Worker**: ComfyUI API + Ostris ai-toolkit (Runs on RunPod GPU)

## Features
- Dataset Manager (Florence-2 auto-captioning)
- Character Training (FLUX.1 LoRA)
- Image Generation (ComfyUI)
- Video API Integration (Luma, Runway)
- Content Calendar & Social Media Captioning

## Deployment (RunPod)

1. Provision a RunPod instance with a GPU (e.g., RTX 4090, A6000, L40S).
2. Clone this repository or transfer the files via SCP.
3. Run `make deploy`.

This will start the entire Docker Compose stack (API, UI, Database, Redis, Celery, and ComfyUI).

## Local Development (Frontend)

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at `http://localhost:5173`.
