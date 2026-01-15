from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="AI Deduplication Service",
    description="Face recognition and similarity matching for voter deduplication",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {
        "service": "AI Deduplication Service",
        "status": "operational",
        "features": [
            "Face Recognition (FaceNet)",
            "Phonetic Name Matching",
            "Date of Birth Verification",
            "Multi-factor Deduplication"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)