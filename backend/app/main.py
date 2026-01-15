# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.database.base import Base, engine, blockchain_engine
from app.api.routes import registration, transfer, voting, admin
import os

# Create tables
Base.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=blockchain_engine)

app = FastAPI(
    title=f"Voter Management System - {settings.STATE_NAME}",
    description="Blockchain-based Electoral Roll Management System",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage directory
os.makedirs(settings.PHOTO_STORAGE_PATH, exist_ok=True)

# Mount static files for photos
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Include routers
app.include_router(registration.router, prefix="/api/registration", tags=["Registration"])
app.include_router(transfer.router, prefix="/api/transfer", tags=["Transfer"])
app.include_router(voting.router, prefix="/api/voting", tags=["Voting"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {
        "service": "Voter Management System",
        "state": settings.STATE_NAME,
        "state_id": settings.STATE_ID,
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)