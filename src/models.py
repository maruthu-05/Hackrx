"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    """Request model for document queries"""
    documents: str  # URL to document
    questions: List[str]

class QueryResponse(BaseModel):
    """Response model for query results"""
    answers: List[str]

class DocumentChunk(BaseModel):
    """Model for document chunks with metadata"""
    content: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    chunk_id: str
    
class ClauseMatch(BaseModel):
    """Model for matched clauses"""
    content: str
    relevance_score: float
    source_location: str
    context: str

class EvaluationResult(BaseModel):
    """Model for logic evaluation results"""
    answer: str
    confidence: float
    reasoning: str
    supporting_clauses: List[ClauseMatch]