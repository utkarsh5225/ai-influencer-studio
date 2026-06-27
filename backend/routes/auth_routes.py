from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth import verify_password, create_access_token, get_password_hash
from datetime import timedelta

router = APIRouter(tags=["Authentication"])

# Hardcoded admin for RunPod simple deployment
ADMIN_USER = "admin"
ADMIN_PASS_HASH = get_password_hash("runpod123") # Default password, users should change this

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real app, verify against the DB
    if form_data.username != ADMIN_USER or not verify_password(form_data.password, ADMIN_PASS_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=60 * 24 * 7)
    access_token = create_access_token(
        data={"sub": ADMIN_USER}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
