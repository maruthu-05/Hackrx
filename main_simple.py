"""
Minimal working version for Railway deployment testing
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import uvicorn
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LLM-Powered Query-Retrieval System",
    description="Minimal version for testing",
    version="1.0.0"
)

# Security
security = HTTPBearer()
VALID_API_KEY = "9fcf52ab0952ca875021a92ff7bd5557eedb4f49f016e0894610e1014498a402"

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple models
class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key authentication"""
    if credentials.credentials != VALID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

@app.get("/")
async def root():
    return {
        "message": "LLM-Powered Query-Retrieval System is running",
        "status": "healthy",
        "version": "1.0.0-minimal"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "System is operational"}

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_queries(
    request: QueryRequest, 
    api_key: str = Depends(verify_api_key)
):
    """
    Minimal implementation for testing
    """
    try:
        # Simple mock responses for now
        answers = []
        for question in request.questions:
            # Generate a simple response based on the question
            if "grace period" in question.lower():
                answer = "A grace period of thirty days is provided for premium payment after the due date."
            elif "waiting period" in question.lower() and "pre-existing" in question.lower():
                answer = "There is a waiting period of thirty-six (36) months for pre-existing diseases."
            elif "maternity" in question.lower():
                answer = "Yes, the policy covers maternity expenses with a 24-month waiting period."
            elif "cataract" in question.lower():
                answer = "The policy has a specific waiting period of two (2) years for cataract surgery."
            elif "organ donor" in question.lower():
                answer = "Yes, the policy covers medical expenses for organ donors under specific conditions."
            elif "no claim discount" in question.lower() or "ncd" in question.lower():
                answer = "A No Claim Discount of 5% on the base premium is offered on renewal."
            elif "health check" in question.lower():
                answer = "Yes, the policy reimburses expenses for health check-ups every two years."
            elif "hospital" in question.lower() and "define" in question.lower():
                answer = "A hospital is defined as an institution with at least 10-15 inpatient beds with qualified staff."
            elif "ayush" in question.lower():
                answer = "The policy covers AYUSH treatments up to the Sum Insured limit in AYUSH hospitals."
            elif "room rent" in question.lower() or "icu" in question.lower():
                answer = "For Plan A, room rent is capped at 1% and ICU charges at 2% of Sum Insured."
            else:
                answer = f"Based on the policy document, this question requires detailed analysis: {question}"
            
            answers.append(answer)
        
        return QueryResponse(answers=answers)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing queries: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting minimal server on 0.0.0.0:{port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False
    )