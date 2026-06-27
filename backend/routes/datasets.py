import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from services.image import process_image
from services.caption import generate_caption, save_caption

router = APIRouter(prefix="/datasets", tags=["Datasets"])

DATASETS_DIR = "/data/datasets"
# Fallback for local dev without docker
if not os.path.exists(DATASETS_DIR):
    DATASETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "datasets")

@router.post("/create")
def create_dataset(name: str = Form(...)):
    """Creates a new empty dataset."""
    path = os.path.join(DATASETS_DIR, name)
    if os.path.exists(path):
        raise HTTPException(status_code=400, detail="Dataset already exists")
    os.makedirs(path)
    return {"status": "success", "dataset": name}

@router.get("/")
def list_datasets():
    """Lists all datasets and their image counts."""
    if not os.path.exists(DATASETS_DIR):
        return []
    
    datasets = []
    for d in os.listdir(DATASETS_DIR):
        path = os.path.join(DATASETS_DIR, d)
        if os.path.isdir(path):
            images = [f for f in os.listdir(path) if f.endswith((".png", ".jpg", ".jpeg"))]
            datasets.append({
                "name": d,
                "image_count": len(images)
            })
    return datasets

@router.post("/{dataset_name}/upload")
async def upload_images(dataset_name: str, files: List[UploadFile] = File(...)):
    """Uploads and processes images for a dataset."""
    path = os.path.join(DATASETS_DIR, dataset_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    uploaded = []
    for file in files:
        file_path = os.path.join(path, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process image (crop, resize, convert)
        success, new_path = process_image(file_path)
        if success:
            uploaded.append(new_path)
            
    return {"status": "success", "processed": len(uploaded)}

@router.post("/{dataset_name}/caption")
def auto_caption_dataset(dataset_name: str):
    """Generates captions for all images in the dataset."""
    path = os.path.join(DATASETS_DIR, dataset_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    images = [f for f in os.listdir(path) if f.endswith(".png")]
    for img in images:
        img_path = os.path.join(path, img)
        caption = generate_caption(img_path)
        save_caption(img_path, caption)
        
    return {"status": "success", "captioned": len(images)}
