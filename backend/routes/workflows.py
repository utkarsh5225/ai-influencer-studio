import os
import json
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/workflows", tags=["Workflows"])

WORKFLOWS_DIR = "/data/workflows"
if not os.path.exists(WORKFLOWS_DIR):
    WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "workflows")

class WorkflowData(BaseModel):
    name: str
    description: str = ""
    workflow_json: Dict[str, Any]

@router.get("/")
def list_workflows():
    if not os.path.exists(WORKFLOWS_DIR):
        return []
    workflows = []
    for f in os.listdir(WORKFLOWS_DIR):
        if f.endswith(".json"):
            workflows.append(f.replace(".json", ""))
    return workflows

@router.post("/save")
def save_workflow(data: WorkflowData):
    path = os.path.join(WORKFLOWS_DIR, f"{data.name}.json")
    with open(path, "w") as f:
        json.dump(data.workflow_json, f)
    return {"status": "saved", "name": data.name}

@router.get("/{name}")
def get_workflow(name: str):
    path = os.path.join(WORKFLOWS_DIR, f"{name}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Workflow not found")
    with open(path, "r") as f:
        return json.load(f)

@router.post("/upload")
async def upload_workflow(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Must be a JSON file")
    
    path = os.path.join(WORKFLOWS_DIR, file.filename)
    content = await file.read()
    
    try:
        json.loads(content) # validate JSON
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
        
    with open(path, "wb") as f:
        f.write(content)
        
    return {"status": "uploaded", "name": file.filename}
