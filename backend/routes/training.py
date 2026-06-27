from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
import subprocess
import yaml
import threading
import time

router = APIRouter(prefix="/training", tags=["Training"])

# Global state for simplicity (since it's a single-tenant app)
training_state = {
    "status": "idle", # idle, running, success, error
    "progress": 0,
    "log": "Awaiting training command...",
    "job_id": None
}

AI_TOOLKIT_PATH = os.getenv("AI_TOOLKIT_PATH", "/workspace/ai-toolkit")

class TrainingRequest(BaseModel):
    dataset_name: str
    trigger_word: str
    hf_token: str = None
    resolution: int = 1024
    epochs: int = 10
    learning_rate: float = 1e-4
    batch_size: int = 1
    optimizer: str = "adamw8bit"

def run_training(config_dict: dict, job_id: str, hf_token: str = None):
    global training_state
    training_state["status"] = "running"
    training_state["progress"] = 0
    training_state["job_id"] = job_id
    training_state["log"] = "Generating config file...\n"
    
    config_path = f"/tmp/config_{job_id}.yaml"
    try:
        with open(config_path, "w") as f:
            yaml.dump(config_dict, f)
            
        if not os.path.exists(AI_TOOLKIT_PATH):
            training_state["log"] = f"Error: ai-toolkit not found at {AI_TOOLKIT_PATH}\n"
            training_state["status"] = "error"
            return
            
        training_state["log"] = f"Starting ai-toolkit at {AI_TOOLKIT_PATH}...\n"
        
        env_dict = os.environ.copy()
        if hf_token:
            env_dict["HF_TOKEN"] = hf_token
            
        cmd = ["python", os.path.join(AI_TOOLKIT_PATH, "run.py"), config_path]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env_dict)
        
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            training_state["log"] += line
            # Keep log from getting too massive (keep last 5000 chars)
            if len(training_state["log"]) > 5000:
                training_state["log"] = "..." + training_state["log"][-4997:]
                
            # Naive progress parsing for ai-toolkit (e.g. 10/1000)
            if "/" in line and "it" in line:
                try:
                    parts = line.split()[0].split("/")
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        training_state["progress"] = int((int(parts[0]) / int(parts[1])) * 100)
                except:
                    pass
            
        process.stdout.close()
        return_code = process.wait()
        
        if return_code == 0:
            training_state["status"] = "success"
            training_state["progress"] = 100
            training_state["log"] += "\nTraining completed successfully! LoRA saved."
        else:
            training_state["status"] = "error"
            training_state["log"] += f"\nTraining failed with exit code {return_code}"
            
    except Exception as e:
        training_state["status"] = "error"
        training_state["log"] = f"Exception: {str(e)}"
    finally:
        if os.path.exists(config_path):
            os.remove(config_path)

@router.post("/start")
def start_training(req: TrainingRequest, background_tasks: BackgroundTasks):
    global training_state
    if training_state["status"] == "running":
        raise HTTPException(status_code=400, detail="A training job is already running.")
        
    config = {
        "job": "extension",
        "config": {
            "name": f"{req.dataset_name}_lora",
            "process": [
                {
                    "type": "sd_trainer",
                    "training_folder": "/workspace/ai-influencer-studio/data/ComfyUI/models/loras",
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
                            "folder_path": f"/workspace/ai-influencer-studio/data/datasets/{req.dataset_name}",
                            "resolution": [req.resolution, req.resolution],
                            "default_caption": req.trigger_word,
                            "cache_latents_to_disk": True
                        }
                    ],
                    "train": {
                        "batch_size": req.batch_size,
                        "steps": req.epochs * 100,
                        "learning_rate": req.learning_rate,
                        "optimizer": req.optimizer,
                        "noise_scheduler": "flowmatch",
                        "gradient_checkpointing": True
                    },
                    "model": {
                        "name_or_path": "black-forest-labs/FLUX.1-dev",
                        "is_flux": True,
                        "quantize": True,
                        "low_vram": True
                    }
                }
            ]
        }
    }
    
    import uuid
    job_id = str(uuid.uuid4())
    background_tasks.add_task(run_training, config, job_id, req.hf_token)
    return {"status": "started", "job_id": job_id}

@router.get("/status")
def get_training_status():
    global training_state
    return training_state
