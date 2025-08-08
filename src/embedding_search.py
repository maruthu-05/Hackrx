"""
Embedding-based semantic search using FAISS
Handles document indexing and similarity search
"""

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
from src.models import DocumentChunk, ClauseMatch

class EmbeddingSearch:
    """FAISS-based semantic search for document chunks"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.index = None
        self.chunks = []
        self.embeddings = None
        
    async def initialize(self):
        """Initialize the sentence transformer model"""
        print(f"🤖 Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print("✅ Embedding model loaded successfully")
    
    async def build_index(self, chunks: List[DocumentChunk]):
        """
        Build FAISS index from document chunks
        
        Args:
            chunks: List of document chunks to index
        """
        if not self.model:
            await self.initialize()
        
        self.chunks = chunks
        
        # Extract text content for embedding
        texts = [chunk.content for chunk in chunks]
        
        print(f"🔄 Creating embeddings for {len(texts)} chunks...")
        
        # Generate embeddings
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)
        
        # Add embeddings to index
        self.index.add(self.embeddings.astype('float32'))
        
        print(f"✅ FAISS index built with {self.index.ntotal} vectors")
    
    async def search(self, query: str, top_k: int = 5) -> List[ClauseMatch]:
        """
        Search for relevant document chunks using semantic similarity
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of ClauseMatch objects with relevance scores
        """
        if not self.index or not self.model:
            raise Exception("Index not built. Call build_index() first.")
        
        # Encode query
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search index
        try:
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        except Exception as e:
            print(f"❌ FAISS search error: {e}")
            return []
        
        # Convert results to ClauseMatch objects
        matches = []
        
        # Handle empty results
        if len(scores) == 0 or len(indices) == 0:
            print("⚠️ No search results found")
            return matches
            
        # Ensure we have valid results
        if len(scores[0]) == 0 or len(indices[0]) == 0:
            print("⚠️ Empty search results")
            return matches
        
        for score, idx in zip(scores[0], indices[0]):
            # Skip invalid indices
            if idx < 0 or idx >= len(self.chunks):
                print(f"⚠️ Invalid index {idx}, skipping")
                continue
                
            chunk = self.chunks[idx]
            
            match = ClauseMatch(
                content=chunk.content,
                relevance_score=float(score),
                source_location=f"Page {chunk.page_number}" if chunk.page_number else "Unknown",
                context=self._get_context(idx)
            )
            matches.append(match)
        
        return matches
    
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
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else 0
        }