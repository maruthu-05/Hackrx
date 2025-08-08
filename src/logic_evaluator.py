"""
Logic evaluator for generating contextual responses using Google Gemini
Handles decision processing and explainable reasoning
"""

import google.generativeai as genai
import os
from typing import List, Dict, Any
from src.models import ClauseMatch, DocumentChunk, EvaluationResult
import json

class LogicEvaluator:
    """Gemini-powered logic evaluation and response generation"""
    
    def __init__(self):
        # Initialize Gemini client
        api_key = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # System prompt for consistent responses
        self.system_prompt = """You are an expert document analyst specializing in insurance, legal, HR, and compliance documents. 

Your task is to provide accurate, concise answers based on the provided document clauses. Follow these guidelines:

1. ACCURACY: Base your answers strictly on the provided clauses
2. CLARITY: Provide clear, direct answers without unnecessary jargon
3. COMPLETENESS: Include all relevant conditions, limitations, and exceptions
4. STRUCTURE: Organize complex answers with clear conditions and requirements
5. EVIDENCE: Reference specific clauses when making statements

For questions about coverage, benefits, or eligibility:
- State clearly what IS covered/included
- Mention any conditions or requirements
- Note any limitations, exclusions, or waiting periods
- Include specific amounts, percentages, or time periods when mentioned

For yes/no questions:
- Start with a clear "Yes" or "No"
- Follow with the specific conditions or details
- Explain any limitations or exceptions

Always maintain a professional, helpful tone while being precise and factual."""
    
    async def evaluate_and_respond(self, query: str, matched_clauses: List[ClauseMatch], 
                                 document_content: List[DocumentChunk]) -> str:
        """
        Generate contextual response using LLM evaluation
        
        Args:
            query: User query
            matched_clauses: Relevant clauses found by matching
            document_content: Full document content for additional context
            
        Returns:
            Generated response string
        """
        try:
            # Prepare context from matched clauses
            context = self._prepare_context(matched_clauses)
            
            # Create user prompt
            user_prompt = self._create_user_prompt(query, context)
            
            # Generate response using OpenAI
            response = await self._generate_llm_response(user_prompt)
            
            return response
            
        except Exception as e:
            # Fallback to rule-based response if LLM fails
            print(f"⚠️ LLM evaluation failed: {str(e)}")
            return self._generate_fallback_response(query, matched_clauses)
    
    def _prepare_context(self, matched_clauses: List[ClauseMatch]) -> str:
        """Prepare context string from matched clauses"""
        if not matched_clauses:
            return "No relevant clauses found in the document."
        
        context_parts = []
        for i, clause in enumerate(matched_clauses, 1):
            context_parts.append(
                f"Clause {i} (Relevance: {clause.relevance_score:.2f}):\n"
                f"Source: {clause.source_location}\n"
                f"Content: {clause.content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _create_user_prompt(self, query: str, context: str) -> str:
        """Create structured prompt for LLM"""
        return f"""Based on the following document clauses, please answer this question:

QUESTION: {query}

RELEVANT CLAUSES:
{context}

Please provide a clear, accurate answer based solely on the information in these clauses. If the clauses don't contain enough information to fully answer the question, state what information is available and what might be missing."""
    
    async def _generate_llm_response(self, user_prompt: str) -> str:
        """Generate response using Google Gemini"""
        try:
            # Check if API key is configured
            api_key = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
            if api_key == 'your-gemini-api-key-here' or not api_key:
                print("⚠️ Gemini API key not configured, using fallback response")
                return "API key not configured. Please set GEMINI_API_KEY in your .env file."
            
            # Combine system prompt and user prompt for Gemini
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for consistent, factual responses
                max_output_tokens=500,  # Reasonable limit for concise answers
                top_p=0.9
            )
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"⚠️ Gemini API error: {str(e)}")
            # Fall back to rule-based response
            return f"Gemini API error: {str(e)}. Please check your API key and try again."
    
    def _generate_fallback_response(self, query: str, matched_clauses: List[ClauseMatch]) -> str:
        """Generate fallback response using rule-based approach"""
        if not matched_clauses:
            return "I couldn't find relevant information in the document to answer your question."
        
        # Use the highest scoring clause as primary source
        primary_clause = matched_clauses[0]
        
        # Simple rule-based response generation
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['does', 'is', 'are', 'can']):
            # Boolean question
            if any(word in primary_clause.content.lower() for word in ['cover', 'include', 'eligible']):
                response = f"Based on the policy document: {primary_clause.content[:200]}..."
            else:
                response = f"According to the document: {primary_clause.content[:200]}..."
        else:
            # Factual question
            response = f"Based on the policy information: {primary_clause.content[:300]}..."
        
        return response
    
    def _extract_key_information(self, content: str, query: str) -> Dict[str, Any]:
        """Extract key information from clause content"""
        info = {
            'amounts': [],
            'periods': [],
            'conditions': [],
            'exclusions': []
        }
        
        # Extract monetary amounts
        import re
        amounts = re.findall(r'[\$₹][\d,]+(?:\.\d{2})?', content)
        info['amounts'] = amounts
        
        # Extract time periods
        periods = re.findall(r'\d+\s*(?:days?|months?|years?)', content)
        info['periods'] = periods
        
        # Extract conditions (sentences with "if", "provided", "subject to")
        condition_patterns = [
            r'[^.]*(?:if|provided|subject to)[^.]*\.',
            r'[^.]*(?:condition|requirement)[^.]*\.',
        ]
        
        for pattern in condition_patterns:
            conditions = re.findall(pattern, content, re.IGNORECASE)
            info['conditions'].extend(conditions)
        
        # Extract exclusions
        exclusion_patterns = [
            r'[^.]*(?:not covered|exclude|except)[^.]*\.',
            r'[^.]*(?:limitation|restriction)[^.]*\.',
        ]
        
        for pattern in exclusion_patterns:
            exclusions = re.findall(pattern, content, re.IGNORECASE)
            info['exclusions'].extend(exclusions)
        
        return info