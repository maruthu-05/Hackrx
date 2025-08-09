"""
LLM-Powered Intelligent Query-Retrieval System
Main FastAPI application entry point
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
from src.embedding_search import EmbeddingSearch
from src.clause_matcher import ClauseMatcher
from src.logic_evaluator import LogicEvaluator
from src.models import QueryRequest, QueryResponse, DocumentChunk

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
embedding_search = EmbeddingSearch()
clause_matcher = ClauseMatcher()
logic_evaluator = LogicEvaluator()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key authentication"""
    if credentials.credentials != VALID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Initialize system components at module level
async def initialize_system():
    """Initialize system components"""
    try:
        await embedding_search.initialize()
        print("System initialized successfully")
    except Exception as e:
        print(f"Failed to initialize system: {e}")
        raise

# We'll initialize on first request instead of startup

@app.get("/")
async def root():
    return {
        "message": "LLM-Powered Query-Retrieval System is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "detailed_health": "/health/detailed",
            "main_api": "/hackrx/run",
            "docs": "/docs"
        }
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify the system works"""
    try:
        # Test basic functionality without document processing
        test_chunks = [
            DocumentChunk(
                content="This is a test policy document with coverage information.",
                page_number=1,
                chunk_id="test-1"
            ),
            DocumentChunk(
                content="The waiting period for claims is 30 days from policy inception.",
                page_number=1,
                chunk_id="test-2"
            )
        ]
        
        # Test embedding search
        await embedding_search.build_index(test_chunks)
        results = await embedding_search.search("waiting period", top_k=2)
        
        return {
            "status": "success",
            "message": "System test completed successfully",
            "test_results": {
                "chunks_processed": len(test_chunks),
                "search_results": len(results),
                "top_result": results[0].content[:100] + "..." if results else "No results"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"System test failed: {str(e)}"
        }

@app.get("/health")
async def health_check():
    try:
        # Basic health check - just return status
        return {"status": "healthy", "message": "System is operational"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check that tests system components"""
    global _system_initialized
    
    try:
        status = {
            "status": "healthy",
            "components": {
                "server": "running",
                "system_initialized": _system_initialized,
                "document_processor": "ready",
                "embedding_search": "ready",
                "logic_evaluator": "ready"
            }
        }
        
        # Test if we can initialize the system
        if not _system_initialized:
            await initialize_system()
            _system_initialized = True
            status["components"]["system_initialized"] = True
        
        return status
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "components": {
                "server": "running",
                "system_initialized": False,
                "error_details": str(e)
            }
        }

# Global flag to track initialization
_system_initialized = False

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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"  # Accept connections from any IP for deployment
    
    print(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        app,  # Use app directly instead of string
        host=host,
        port=port,
        reload=False  # Disable reload in production
    )