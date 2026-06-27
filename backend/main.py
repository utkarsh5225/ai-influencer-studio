import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import models, datasets, training, generation, workflows, video, captions, calendar, auth_routes
from database import engine, Base
from fastapi.staticfiles import StaticFiles
import os
# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ai_studio")

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Influencer Studio API",
    description="Backend API for the AI Influencer Studio",
    version="1.0.0"
)

# Allow CORS for the local React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount ComfyUI output folder to serve images
output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "ComfyUI", "output")
os.makedirs(output_dir, exist_ok=True)
app.mount("/output", StaticFiles(directory=output_dir), name="output")

app.include_router(auth_routes.router)
app.include_router(models.router)
app.include_router(datasets.router)
app.include_router(training.router)
app.include_router(generation.router)
app.include_router(workflows.router)
app.include_router(video.router)
app.include_router(captions.router)
app.include_router(calendar.router)

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"status": "ok", "message": "AI Influencer Studio API is running"}
