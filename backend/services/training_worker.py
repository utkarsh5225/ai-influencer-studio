import os
import subprocess
import yaml
from celery_app import celery_app

AI_TOOLKIT_PATH = os.getenv("AI_TOOLKIT_PATH", "/workspace/ai-toolkit")
OUTPUT_DIR = "/data/models/loras"
if not os.path.exists(OUTPUT_DIR):
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "models", "loras")

@celery_app.task(bind=True)
def train_lora_task(self, config_dict: dict):
    """
    Celery task to run Ostris ai-toolkit for FLUX LoRA training.
    """
    job_id = self.request.id
    config_path = f"/tmp/config_{job_id}.yaml"
    
    # Save config to file
    with open(config_path, "w") as f:
        yaml.dump(config_dict, f)
        
    self.update_state(state="TRAINING", meta={"progress": 0, "status": "Starting training..."})
    
    try:
        # We would run ai-toolkit here. 
        # python run.py config_path
        # For this prototype, we simulate the subprocess or call it if ai-toolkit exists.
        if os.path.exists(AI_TOOLKIT_PATH):
            cmd = ["python", os.path.join(AI_TOOLKIT_PATH, "run.py"), config_path]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            for line in process.stdout:
                # Parse progress from line (example)
                # if "Steps:" in line: progress = parse(line)
                # self.update_state(...)
                pass
                
            process.wait()
            if process.returncode != 0:
                raise Exception("Training process failed.")
        else:
            # Simulation mode for local testing
            import time
            for i in range(1, 101):
                time.sleep(0.1)
                self.update_state(state="TRAINING", meta={"progress": i, "status": f"Training step {i}/100"})
                
        return {"status": "success", "job_id": job_id, "output": OUTPUT_DIR}
    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise e
    finally:
        if os.path.exists(config_path):
            os.remove(config_path)
