"""
Ultra-lightweight embedding search for Vercel deployment
Uses simple text matching without ML dependencies
"""

import re
from collections import Counter
from typing import List, Dict, Any, Tuple
from src.models import DocumentChunk, ClauseMatch

class EmbeddingSearchLite:
    """Simple text-based search for document chunks"""
    
    def __init__(self):
        self.chunks = []
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
    async def initialize(self):
        """Initialize the search system"""
        pass
    
    async def build_index(self, chunks: List[DocumentChunk]):
        """
        Build simple text index from document chunks
        
        Args:
            chunks: List of document chunks to index
        """
        await self.initialize()
        self.chunks = chunks
    
    async def search(self, query: str, top_k: int = 5) -> List[ClauseMatch]:
        """
        Search for relevant document chunks using simple text matching
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of ClauseMatch objects with relevance scores
        """
        if not self.chunks:
            return []
        
        try:
            # Normalize query
            query_words = self._extract_keywords(query.lower())
            
            # Score each chunk
            scored_chunks = []
            for idx, chunk in enumerate(self.chunks):
                score = self._calculate_similarity(query_words, chunk.content.lower())
                if score > 0:
                    scored_chunks.append((idx, score))
            
            # Sort by score and get top k
            scored_chunks.sort(key=lambda x: x[1], reverse=True)
            top_chunks = scored_chunks[:top_k]
            
            # Convert to ClauseMatch objects
            matches = []
            for idx, score in top_chunks:
                chunk = self.chunks[idx]
                match = ClauseMatch(
                    content=chunk.content,
                    relevance_score=float(score),
                    source_location=f"Page {chunk.page_number}" if chunk.page_number else "Unknown",
                    context=self._get_context(idx)
                )
                matches.append(match)
            
            return matches
            
        except Exception as e:
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text, removing stop words"""
        # Simple tokenization
        words = re.findall(r'\b\w+\b', text)
        # Remove stop words and short words
        keywords = [w for w in words if w not in self.stop_words and len(w) > 2]
        return keywords
    
    def _calculate_similarity(self, query_words: List[str], text: str) -> float:
        """Calculate simple similarity score between query and text"""
        if not query_words:
            return 0.0
        
        text_words = self._extract_keywords(text)
        if not text_words:
            return 0.0
        
        # Count word matches
        matches = 0
        for word in query_words:
            if word in text_words:
                matches += 1
            # Also check for partial matches
            elif any(word in text_word or text_word in word for text_word in text_words):
                matches += 0.5
        
        # Normalize by query length
        return matches / len(query_words)
    
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
        
        total_length = sum(len(chunk.content) for chunk in self.chunks)
        avg_length = total_length / len(self.chunks) if self.chunks else 0
        
        return {
            "total_chunks": len(self.chunks),
            "avg_chunk_length": avg_length,
            "total_pages": len(set(chunk.page_number for chunk in self.chunks if chunk.page_number))
        }