import os
from PIL import Image

def process_image(file_path: str, target_resolution: int = 1024):
    """
    Processes an image: converts to RGB, crops to square, 
    resizes to target_resolution, and saves as PNG.
    """
    try:
        with Image.open(file_path) as img:
            # Convert to RGB (in case of RGBA or palette)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Auto center crop
            width, height = img.size
            min_dim = min(width, height)
            left = (width - min_dim) / 2
            top = (height - min_dim) / 2
            right = (width + min_dim) / 2
            bottom = (height + min_dim) / 2
            
            img = img.crop((left, top, right, bottom))
            
            # Resize
            img = img.resize((target_resolution, target_resolution), Image.Resampling.LANCZOS)
            
            # Save as PNG
            new_path = os.path.splitext(file_path)[0] + ".png"
            img.save(new_path, "PNG")
            
            # Remove original if it wasn't a png
            if file_path != new_path:
                os.remove(file_path)
                
            return True, new_path
    except Exception as e:
        return False, str(e)
