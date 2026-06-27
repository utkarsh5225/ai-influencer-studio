import urllib.request
import urllib.parse
import json
import uuid
import os

COMFY_API_URL = os.getenv("COMFY_URL", "http://comfyui:8188")
if not os.getenv("COMFY_URL"):
    # Fallback for local testing outside docker
    COMFY_API_URL = "http://localhost:8188"

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow, "client_id": str(uuid.uuid4())}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request(f"{COMFY_API_URL}/prompt", data=data)
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode('utf-8')}"}
    except Exception as e:
        return {"error": str(e)}

def get_history(prompt_id):
    req =  urllib.request.Request(f"{COMFY_API_URL}/history/{prompt_id}")
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except Exception as e:
        return {"error": str(e)}

def build_flux_workflow(prompt: str, seed: int, steps: int = 20, lora_name: str = None, lora_strength: float = 1.0, width: int = 1024, height: int = 1024):
    """
    Builds a complete ComfyUI workflow JSON for FLUX.1 dev generation.
    """
    workflow = {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "flux1-dev.safetensors",
                "weight_dtype": "default"
            }
        },
        "2": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "t5xxl_fp16.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "flux"
            }
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "ae.safetensors"
            }
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "batch_size": 1,
                "width": width,
                "height": height
            }
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": ["2", 0]
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "",
                "clip": ["2", 0]
            }
        },
        "7": {
            "class_type": "FluxGuidance",
            "inputs": {
                "guidance": 3.5,
                "conditioning": ["5", 0]
            }
        },
        "8": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["7", 0],
                "negative": ["6", 0],
                "latent_image": ["4", 0]
            }
        },
        "9": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["8", 0],
                "vae": ["3", 0]
            }
        },
        "10": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "AI_Influencer",
                "images": ["9", 0]
            }
        }
    }
    
    if lora_name:
        workflow["20"] = {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": lora_name,
                "strength_model": lora_strength,
                "strength_clip": lora_strength,
                "model": ["1", 0],
                "clip": ["2", 0]
            }
        }
        # Update KSampler to use Lora
        workflow["8"]["inputs"]["model"] = ["20", 0]
        workflow["5"]["inputs"]["clip"] = ["20", 1]
        workflow["6"]["inputs"]["clip"] = ["20", 1]
        
    return workflow
