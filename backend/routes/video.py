import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter(prefix="/video", tags=["Video"])

# Video API Keys would normally be in .env
LUMA_API_KEY = os.getenv("LUMA_API_KEY", "")
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY", "")

class VideoJobRequest(BaseModel):
    image_url: str
    prompt: str
    provider: str = "luma" # 'luma', 'runway', 'pika'
    duration: int = 5

# In-memory store for mock jobs
jobs_db = {}

@router.post("/generate")
def create_video_job(req: VideoJobRequest):
    """
    Submits an Image-to-Video job to an external provider.
    Currently mocked if API keys are missing.
    """
    job_id = str(uuid.uuid4())
    
    # Mocking the API call
    jobs_db[job_id] = {
        "status": "processing",
        "provider": req.provider,
        "image_url": req.image_url,
        "progress": 0,
        "video_url": None
    }
    
    return {"status": "queued", "job_id": job_id}

@router.get("/status/{job_id}")
def check_video_status(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = jobs_db[job_id]
    
    # Simulate progress
    if job["status"] == "processing":
        job["progress"] += 20
        if job["progress"] >= 100:
            job["status"] = "completed"
            job["video_url"] = f"https://mock-video-cdn.com/{job_id}.mp4"
            
    return job
