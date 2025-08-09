"""
Document processor for handling PDFs, DOCX, and email documents
Extracts and structures content for further processing
"""

import requests
import PyPDF2
from docx import Document
import io
import re
import uuid
from typing import List, Dict, Any
from src.models import DocumentChunk

class DocumentProcessor:
    """Handles document parsing and content extraction"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc']
    
    async def process_document(self, document_url: str) -> List[DocumentChunk]:
        """
        Process document from URL and extract structured content
        
        Args:
            document_url: URL to the document
            
        Returns:
            List of DocumentChunk objects with extracted content
        """
        try:
            # Download document
            response = requests.get(document_url, timeout=30)
            response.raise_for_status()
            
            # Determine file type from URL or content-type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'pdf' in content_type or document_url.lower().endswith('.pdf'):
                chunks = await self._process_pdf(response.content)
            elif 'word' in content_type or document_url.lower().endswith(('.docx', '.doc')):
                chunks = await self._process_docx(response.content)
            else:
                # Try to process as text
                chunks = await self._process_text(response.text)
            

            
            # Ensure we have at least some content
            if not chunks:
                # Create a fallback chunk
                chunks = [DocumentChunk(
                    content="Document processed but no readable content found.",
                    page_number=1,
                    chunk_id=str(uuid.uuid4())
                )]
            
            return chunks
                
        except Exception as e:
            # Return a fallback chunk instead of raising
            return [DocumentChunk(
                content=f"Error processing document: {str(e)}",
                page_number=1,
                chunk_id=str(uuid.uuid4())
            )]
    
    async def _process_pdf(self, content: bytes) -> List[DocumentChunk]:
        """Extract content from PDF document"""
        chunks = []
        
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    # Split page into logical chunks
                    page_chunks = self._split_into_chunks(text, page_num + 1)
                    chunks.extend(page_chunks)
                    
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
        
        return chunks
    
    async def _process_docx(self, content: bytes) -> List[DocumentChunk]:
        """Extract content from DOCX document"""
        chunks = []
        
        try:
            doc_file = io.BytesIO(content)
            doc = Document(doc_file)
            
            current_section = "Document"
            page_num = 1
            
            for para in doc.paragraphs:
                if para.text.strip():
                    # Check if this is a heading/section
                    if self._is_heading(para.text):
                        current_section = para.text.strip()
                    
                    chunk = DocumentChunk(
                        content=para.text.strip(),
                        page_number=page_num,
                        section=current_section,
                        chunk_id=str(uuid.uuid4())
                    )
                    chunks.append(chunk)
                    
        except Exception as e:
            raise Exception(f"Error processing DOCX: {str(e)}")
        
        return chunks
    
    async def _process_text(self, content: str) -> List[DocumentChunk]:
        """Process plain text content"""
        chunks = self._split_into_chunks(content)
        return chunks
    
    def _split_into_chunks(self, text: str, page_num: int = 1) -> List[DocumentChunk]:
        """Split text into meaningful chunks for processing"""
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            if len(para) < 50:  # Skip very short paragraphs
                continue
                
            # If paragraph is too long, split by sentences
            if len(para) > 1000:
                sentences = re.split(r'[.!?]+', para)
                current_chunk = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                        
                    if len(current_chunk + sentence) > 800:
                        if current_chunk:
                            chunks.append(DocumentChunk(
                                content=current_chunk.strip(),
                                page_number=page_num,
                                chunk_id=str(uuid.uuid4())
                            ))
                        current_chunk = sentence
                    else:
                        current_chunk += ". " + sentence if current_chunk else sentence
                
                if current_chunk:
                    chunks.append(DocumentChunk(
                        content=current_chunk.strip(),
                        page_number=page_num,
                        chunk_id=str(uuid.uuid4())
                    ))
            else:
                chunks.append(DocumentChunk(
                    content=para,
                    page_number=page_num,
                    chunk_id=str(uuid.uuid4())
                ))
        
        return chunks
    
    def _is_heading(self, text: str) -> bool:
        """Determine if text is likely a heading/section title"""
        text = text.strip()
        
        # Check for common heading patterns
        heading_patterns = [
            r'^[A-Z\s]+$',  # ALL CAPS
            r'^\d+\.\s+[A-Z]',  # Numbered sections
            r'^[A-Z][a-z\s]+:$',  # Title with colon
        ]
        
        for pattern in heading_patterns:
            if re.match(pattern, text):
                return True
                
        return len(text) < 100 and text.isupper()