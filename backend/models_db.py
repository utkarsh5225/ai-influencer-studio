from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=True)

class TrainingRun(Base):
    __tablename__ = "training_runs"
    id = Column(String, primary_key=True, index=True)
    dataset_name = Column(String)
    model_name = Column(String)
    status = Column(String)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class GeneratedImage(Base):
    __tablename__ = "generated_images"
    id = Column(String, primary_key=True, index=True)
    file_path = Column(String)
    prompt = Column(String)
    negative_prompt = Column(String)
    seed = Column(Integer)
    lora_used = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
