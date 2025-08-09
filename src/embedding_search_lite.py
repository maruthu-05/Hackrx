"""
Lightweight embedding search using TF-IDF for Vercel deployment
Alternative to sentence-transformers for serverless environments
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
from src.models import DocumentChunk, ClauseMatch

class EmbeddingSearchLite:
    """TF-IDF based semantic search for document chunks"""
    
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.chunks = []
        
    async def initialize(self):
        """Initialize the TF-IDF vectorizer"""
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
    
    async def build_index(self, chunks: List[DocumentChunk]):
        """
        Build TF-IDF index from document chunks
        
        Args:
            chunks: List of document chunks to index
        """
        if not self.vectorizer:
            await self.initialize()
        
        self.chunks = chunks
        
        # Extract text content for vectorization
        texts = [chunk.content for chunk in chunks]
        
        # Create TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
    
    async def search(self, query: str, top_k: int = 5) -> List[ClauseMatch]:
        """
        Search for relevant document chunks using TF-IDF similarity
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of ClauseMatch objects with relevance scores
        """
        if self.tfidf_matrix is None or not self.vectorizer:
            return []
        
        try:
            # Vectorize query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Get top k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Convert results to ClauseMatch objects
            matches = []
            for idx in top_indices:
                if idx < len(self.chunks) and similarities[idx] > 0:
                    chunk = self.chunks[idx]
                    
                    match = ClauseMatch(
                        content=chunk.content,
                        relevance_score=float(similarities[idx]),
                        source_location=f"Page {chunk.page_number}" if chunk.page_number else "Unknown",
                        context=self._get_context(idx)
                    )
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            return []
    
    def _get_context(self, chunk_idx: int, context_window: int = 1) -> str:
        """
        Get surrounding context for a chunk
        
        Args:
            chunk_idx: Index of the target chunk
            context_window: Number of chunks before/after to include
            
        Returns:
            Context string with surrounding chunks
        """
        context_parts = []
        
        # Add previous chunks
        for i in range(max(0, chunk_idx - context_window), chunk_idx):
            context_parts.append(f"[Previous] {self.chunks[i].content[:100]}...")
        
        # Add current chunk
        context_parts.append(f"[Current] {self.chunks[chunk_idx].content}")
        
        # Add next chunks
        for i in range(chunk_idx + 1, min(len(self.chunks), chunk_idx + context_window + 1)):
            context_parts.append(f"[Next] {self.chunks[i].content[:100]}...")
        
        return " ".join(context_parts)
    
    def get_chunk_statistics(self) -> Dict[str, Any]:
        """Get statistics about indexed chunks"""
        if not self.chunks:
            return {"total_chunks": 0}
        
        return {
            "total_chunks": len(self.chunks),
            "avg_chunk_length": np.mean([len(chunk.content) for chunk in self.chunks]),
            "total_pages": len(set(chunk.page_number for chunk in self.chunks if chunk.page_number)),
            "vocabulary_size": len(self.vectorizer.vocabulary_) if self.vectorizer else 0
        }