from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.comfy import queue_prompt, build_flux_workflow, get_history

router = APIRouter(prefix="/generation", tags=["Generation"])

class GenerationRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    seed: int = -1
    cfg: float = 1.0
    steps: int = 20
    sampler: str = "euler"
    scheduler: str = "simple"
    width: int = 1024
    height: int = 1024
    batch_size: int = 1
    lora_name: Optional[str] = None
    lora_strength: float = 1.0

@router.post("/generate")
def generate_image(req: GenerationRequest):
    import random
    seed = req.seed if req.seed != -1 else random.randint(1, 2**32-1)
    
    workflow = build_flux_workflow(
        prompt=req.prompt,
        seed=seed,
        steps=req.steps,
        lora_name=req.lora_name,
        lora_strength=req.lora_strength,
        width=req.width,
        height=req.height
    )
    
    response = queue_prompt(workflow)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
        
    return {
        "status": "queued",
        "prompt_id": response.get("prompt_id"),
        "seed": seed
    }

@router.get("/status/{prompt_id}")
def check_generation_status(prompt_id: str):
    history = get_history(prompt_id)
    if "error" in history:
        return {"status": "error", "message": history["error"]}
        
    if prompt_id in history:
        # Generation is complete
        outputs = []
        node_outputs = history[prompt_id].get("outputs", {})
        for node_id, node_output in node_outputs.items():
            if 'images' in node_output:
                for img in node_output['images']:
                    outputs.append(f"/output/{img['filename']}")
        return {"status": "complete", "images": outputs}
    else:
        return {"status": "pending"}
