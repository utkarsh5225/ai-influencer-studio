import os
from typing import List, Dict
from fastapi import APIRouter

router = APIRouter(prefix="/models", tags=["Models"])

MODELS_DIR = "/data/models"

# Map of model types to their respective subdirectories in ComfyUI
MODEL_DIRS = {
    "unet": "unet",          # For FLUX unet models
    "loras": "loras",
    "vae": "vae",
    "clip": "clip",          # For text encoders
    "controlnet": "controlnet",
    "upscale": "upscale_models"
}

def scan_directory(sub_dir: str) -> List[Dict]:
    """Scans a model directory and returns a list of files."""
    path = os.path.join(MODELS_DIR, sub_dir)
    # Fallback to local path if not in docker
    if not os.path.exists(MODELS_DIR):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "models", sub_dir)
        
    if not os.path.exists(path):
        return []
        
    files = []
    for f in os.listdir(path):
        if f.endswith((".safetensors", ".pt", ".pth", ".ckpt", ".sft")):
            full_path = os.path.join(path, f)
            size_mb = round(os.path.getsize(full_path) / (1024 * 1024), 2)
            files.append({
                "name": f,
                "size_mb": size_mb,
                "type": sub_dir
            })
    return files

@router.get("/")
def list_all_models():
    """Lists all models across all categories."""
    models = {}
    for model_type, sub_dir in MODEL_DIRS.items():
        models[model_type] = scan_directory(sub_dir)
    return models

@router.get("/missing")
def check_missing_models():
    """Checks if essential models like FLUX.1 are missing."""
    unets = scan_directory("unet")
    clips = scan_directory("clip")
    vaes = scan_directory("vae")
    
    missing = []
    if not any("flux1-dev" in u["name"].lower() for u in unets):
        missing.append("FLUX.1-dev UNET")
        
    if not any("t5xxl" in c["name"].lower() for c in clips):
        missing.append("T5XXL Text Encoder")
        
    if not any("clip_l" in c["name"].lower() for c in clips):
        missing.append("CLIP L Text Encoder")
        
    if not any("ae" in v["name"].lower() for v in vaes):
        missing.append("FLUX VAE (ae.safetensors)")
        
    return {
        "status": "ok" if not missing else "missing_core_models",
        "missing_models": missing,
        "instructions": "Please download the missing models and place them in the respective data/models/ folders."
    }
