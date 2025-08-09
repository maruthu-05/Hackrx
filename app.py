"""
Ultra-minimal FastAPI app for Railway deployment testing
"""

from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Hello from Railway!",
        "status": "healthy",
        "port": os.getenv("PORT", "8000")
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)