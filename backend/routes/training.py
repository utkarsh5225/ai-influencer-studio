from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.training_worker import train_lora_task
from celery.result import AsyncResult

router = APIRouter(prefix="/training", tags=["Training"])

class TrainingRequest(BaseModel):
    dataset_name: str
    trigger_word: str
    resolution: int = 1024
    epochs: int = 10
    learning_rate: float = 1e-4
    batch_size: int = 1
    optimizer: str = "adamw8bit"

@router.post("/start")
def start_training(req: TrainingRequest):
    """Starts a new LoRA training job using ai-toolkit."""
    # Build ai-toolkit config structure
    config = {
        "job": "extension",
        "config": {
            "name": f"{req.dataset_name}_lora",
            "process": [
                {
                    "type": "sd_trainer",
                    "training_folder": "/data/models/loras",
                    "device": "cuda:0",
                    "network": {
                        "type": "lora",
                        "linear": 16,
                        "linear_alpha": 16
                    },
                    "save": {
                        "dtype": "float16",
                        "save_every": req.epochs // 2,
                        "max_step_saves_to_keep": 2
                    },
                    "datasets": [
                        {
                            "folder_path": f"/data/datasets/{req.dataset_name}",
                            "caption_ext": "txt",
                            "resolution": [req.resolution, req.resolution],
                            "default_caption": req.trigger_word
                        }
                    ],
                    "train": {
                        "batch_size": req.batch_size,
                        "steps": req.epochs * 100, # estimation
                        "learning_rate": req.learning_rate,
                        "optimizer": req.optimizer,
                        "noise_scheduler": "flowmatch"
                    },
                    "model": {
                        "name_or_path": "/data/models/unet/flux1-dev.safetensors",
                        "is_flux": True,
                        "quantize": True
                    }
                }
            ]
        }
    }
    
    # Queue task
    task = train_lora_task.delay(config)
    return {"status": "started", "job_id": task.id}

@router.get("/status/{job_id}")
def get_training_status(job_id: str):
    """Gets the status of a training job."""
    res = AsyncResult(job_id)
    if res.state == 'PENDING':
        return {"status": "PENDING"}
    elif res.state != 'FAILURE':
        return {
            "status": res.state,
            "info": res.info # Contains progress
        }
    else:
        return {
            "status": res.state,
            "error": str(res.info)
        }
