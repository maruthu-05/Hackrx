"""
LLM-Powered Intelligent Query-Retrieval System - Vercel Version
Optimized for serverless deployment with lighter dependencies
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv

from src.document_processor import DocumentProcessor
from src.embedding_search_lite import EmbeddingSearchLite  # Use lite version
from src.clause_matcher import ClauseMatcher
from src.logic_evaluator import LogicEvaluator
from src.models import QueryRequest, QueryResponse

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LLM-Powered Query-Retrieval System",
    description="Intelligent document processing and query system for insurance, legal, HR, and compliance domains",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Valid API key (in production, store this securely)
VALID_API_KEY = "9fcf52ab0952ca875021a92ff7bd5557eedb4f49f016e0894610e1014498a402"

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system components
document_processor = DocumentProcessor()
embedding_search = EmbeddingSearchLite()  # Use lite version
clause_matcher = ClauseMatcher()
logic_evaluator = LogicEvaluator()

# Global flag to track initialization
_system_initialized = False

async def initialize_system():
    """Initialize system components"""
    await embedding_search.initialize()

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
    return {"message": "LLM-Powered Query-Retrieval System is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "System is operational"}

@app.post("/hackrx/run", response_model=QueryResponse)
async def process_queries(
    request: QueryRequest, 
    api_key: str = Depends(verify_api_key)
):
    """
    Main endpoint for processing document queries
    Implements the complete workflow: Parse -> Embed -> Match -> Evaluate -> Respond
    
    Required format:
    - POST /hackrx/run
    - Authorization: Bearer <api_key>
    - Content-Type: application/json
    """
    global _system_initialized
    
    try:
        # Initialize system on first request
        if not _system_initialized:
            await initialize_system()
            _system_initialized = True
        
        # Step 1: Process documents
        document_content = await document_processor.process_document(request.documents)
        
        # Step 2: Create embeddings and build search index
        await embedding_search.build_index(document_content)
        
        # Step 3: Process each query
        answers = []
        for question in request.questions:
            try:
                # Retrieve relevant clauses
                relevant_clauses = await embedding_search.search(question, top_k=5)
                
                # Match and evaluate clauses
                matched_clauses = clause_matcher.match_clauses(question, relevant_clauses)
                
                # Generate answer using logic evaluator
                answer = await logic_evaluator.evaluate_and_respond(
                    question, matched_clauses, document_content
                )
                
                answers.append(answer)
                
            except Exception as e:
                # Provide fallback answer
                answers.append(f"Unable to process this question: {str(e)}")
        
        return QueryResponse(answers=answers)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing queries: {str(e)}"
        )

# Vercel handler
handler = app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    uvicorn.run(
        "main_vercel:app",
        host=host,
        port=port,
        reload=False
    )