import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import models, datasets, training, generation, workflows, video, captions, calendar, auth_routes
from database import engine, Base

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

app.include_router(auth_routes.router)
app.include_router(models.router)
app.include_router(datasets.router)
app.include_router(training.router)
app.include_router(generation.router)
app.include_router(workflows.router)
app.include_router(video.router)
app.include_router(captions.router)
app.include_router(calendar.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Influencer Studio API is running"}
