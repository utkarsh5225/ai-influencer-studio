import os
import json
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/calendar", tags=["Calendar"])

CALENDAR_DIR = "/data/calendar"
if not os.path.exists(CALENDAR_DIR):
    CALENDAR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "calendar")

class ScheduledPost(BaseModel):
    image_url: str
    caption: str
    platform: str
    scheduled_time: str # ISO 8601

@router.get("/")
def get_schedule():
    """Returns all scheduled posts."""
    path = os.path.join(CALENDAR_DIR, "schedule.json")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

@router.post("/schedule")
def schedule_post(post: ScheduledPost):
    """Schedules a post to be published."""
    path = os.path.join(CALENDAR_DIR, "schedule.json")
    schedule = []
    if os.path.exists(path):
        with open(path, "r") as f:
            schedule = json.load(f)
            
    post_dict = post.model_dump()
    post_dict["id"] = str(uuid.uuid4())
    post_dict["status"] = "scheduled"
    
    schedule.append(post_dict)
    
    with open(path, "w") as f:
        json.dump(schedule, f)
        
    return {"status": "scheduled", "id": post_dict["id"]}

@router.delete("/{post_id}")
def delete_scheduled_post(post_id: str):
    path = os.path.join(CALENDAR_DIR, "schedule.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Schedule not found")
        
    with open(path, "r") as f:
        schedule = json.load(f)
        
    new_schedule = [p for p in schedule if p.get("id") != post_id]
    
    if len(new_schedule) == len(schedule):
        raise HTTPException(status_code=404, detail="Post not found")
        
    with open(path, "w") as f:
        json.dump(new_schedule, f)
        
    return {"status": "deleted"}
