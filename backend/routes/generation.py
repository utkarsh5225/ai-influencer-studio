from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
import websockets
import os
import uuid
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
    
    client_id = str(uuid.uuid4())
    
    response = queue_prompt(workflow, client_id=client_id)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
        
    return {
        "status": "queued",
        "prompt_id": response.get("prompt_id"),
        "client_id": client_id,
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

COMFY_WS_URL = os.getenv("COMFY_WS_URL", "ws://127.0.0.1:8188/ws")

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    comfy_url = f"{COMFY_WS_URL}?clientId={client_id}"
    try:
        async with websockets.connect(comfy_url) as comfy_ws:
            async for message in comfy_ws:
                await websocket.send_text(message)
    except websockets.exceptions.ConnectionClosed:
        pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass
