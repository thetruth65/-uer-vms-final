from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from datetime import timedelta

router = APIRouter()

# Mock Database of Users (For Hackathon ease - replace with DB table in production)
FAKE_USERS_DB = {
    "admin": {
        "username": "admin",
        # Hash for "admin123"
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "role": "admin"
    }
}

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS_DB.get(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # In production use verify_password(form_data.password, user['hashed_password'])
    # For simple demo if you don't want to deal with hash generation:
    if form_data.password != "admin123": 
        raise HTTPException(status_code=400, detail="Incorrect password")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}