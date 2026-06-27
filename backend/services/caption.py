import os

# We will load Florence-2 lazily to avoid heavy memory usage at startup.
# In a real production setup, this would be deployed as a separate worker or managed by Celery.
_model = None
_processor = None

def load_florence_model():
    global _model, _processor
    if _model is None:
        try:
            from transformers import AutoProcessor, AutoModelForCausalLM
            from PIL import Image
            
            # We use a smaller model for local development/RunPod unless specified otherwise.
            model_id = "microsoft/Florence-2-base" 
            _processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
            _model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True).eval()
            print("Loaded Florence-2 for captioning.")
        except ImportError:
            print("Transformers not installed properly for captioning.")
            pass

def generate_caption(image_path: str) -> str:
    """Generates a caption for an image using Florence-2."""
    load_florence_model()
    if _model is None or _processor is None:
        return "A photo of a person." # Fallback for local testing if no GPU/transformers
    
    from PIL import Image
    try:
        image = Image.open(image_path).convert("RGB")
        prompt = "<DETAILED_CAPTION>"
        
        inputs = _processor(text=prompt, images=image, return_tensors="pt")
        
        generated_ids = _model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            do_sample=False,
            num_beams=3
        )
        generated_text = _processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        
        parsed_answer = _processor.post_process_generation(generated_text, task=prompt, image_size=(image.width, image.height))
        return parsed_answer.get("<DETAILED_CAPTION>", "A photo.")
    except Exception as e:
        return f"Error generating caption: {str(e)}"

def save_caption(image_path: str, caption: str):
    """Saves the caption in a .txt file alongside the image."""
    txt_path = os.path.splitext(image_path)[0] + ".txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(caption)
