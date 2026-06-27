from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/captions", tags=["Captions"])

class CaptionRequest(BaseModel):
    image_description: str
    platform: str = "instagram" # instagram, tiktok, threads, x, youtube
    tone: str = "engaging" # professional, funny, engaging, edgy

@router.post("/generate")
def generate_social_caption(req: CaptionRequest):
    """
    Generates social media captions.
    In a real app, this would call an LLM (OpenAI, Anthropic, or Local Llama).
    """
    # Mocked LLM response
    hashtags = "#AIinfluencer #virtualmodel #digitalart"
    
    if req.platform == "instagram":
        text = f"Living my best digital life ✨ {req.image_description}. Drop a comment if you're feeling this vibe! 👇\n\n{hashtags}"
    elif req.platform == "x":
        text = f"Just generated this: {req.image_description}. The future of AI is crazy. {hashtags}"
    elif req.platform == "tiktok":
        text = f"POV: you're an AI model. {req.image_description} 🤖✨ {hashtags} #fyp"
    else:
        text = f"{req.image_description}\n\n{hashtags}"
        
    return {
        "status": "success",
        "platform": req.platform,
        "caption": text,
        "tone": req.tone
    }
