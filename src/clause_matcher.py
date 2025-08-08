"""
Clause matching and semantic similarity processing
Handles advanced matching logic for legal/insurance documents
"""

import re
from typing import List, Dict, Any
from src.models import ClauseMatch
import numpy as np

class ClauseMatcher:
    """Advanced clause matching with domain-specific logic"""
    
    def __init__(self):
        # Domain-specific keywords for different categories
        self.domain_keywords = {
            'insurance': {
                'coverage': ['cover', 'coverage', 'covered', 'benefit', 'indemnify', 'reimburse'],
                'exclusions': ['exclude', 'exclusion', 'not covered', 'except', 'limitation'],
                'conditions': ['condition', 'requirement', 'eligibility', 'qualify', 'subject to'],
                'waiting_period': ['waiting period', 'wait', 'months', 'continuous coverage'],
                'limits': ['limit', 'maximum', 'cap', 'up to', 'not exceeding'],
                'definitions': ['means', 'defined as', 'refers to', 'includes', 'definition']
            },
            'legal': {
                'obligations': ['shall', 'must', 'required', 'obligation', 'duty'],
                'rights': ['right', 'entitled', 'may', 'permitted', 'authorized'],
                'penalties': ['penalty', 'fine', 'damages', 'breach', 'violation'],
                'terms': ['term', 'period', 'duration', 'effective', 'commence']
            },
            'hr': {
                'benefits': ['benefit', 'compensation', 'allowance', 'reimbursement'],
                'policies': ['policy', 'procedure', 'guideline', 'rule', 'regulation'],
                'leave': ['leave', 'vacation', 'sick', 'absence', 'time off'],
                'performance': ['performance', 'evaluation', 'review', 'assessment']
            }
        }
    
    def match_clauses(self, query: str, retrieved_clauses: List[ClauseMatch]) -> List[ClauseMatch]:
        """
        Enhanced clause matching with domain-specific logic
        
        Args:
            query: User query
            retrieved_clauses: Initial retrieved clauses from embedding search
            
        Returns:
            Refined and scored clause matches
        """
        # Analyze query intent and domain
        query_analysis = self._analyze_query(query)
        
        # Re-score clauses based on domain-specific matching
        enhanced_clauses = []
        
        for clause in retrieved_clauses:
            # Calculate enhanced relevance score
            enhanced_score = self._calculate_enhanced_score(
                query, clause, query_analysis
            )
            
            # Create enhanced clause match
            enhanced_clause = ClauseMatch(
                content=clause.content,
                relevance_score=enhanced_score,
                source_location=clause.source_location,
                context=clause.context
            )
            
            enhanced_clauses.append(enhanced_clause)
        
        # Sort by enhanced relevance score
        enhanced_clauses.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Filter out low-relevance clauses
        threshold = 0.3
        filtered_clauses = [c for c in enhanced_clauses if c.relevance_score > threshold]
        
        return filtered_clauses[:5]  # Return top 5 most relevant
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to understand intent and domain
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with query analysis results
        """
        query_lower = query.lower()
        
        analysis = {
            'domain': 'general',
            'intent': 'information',
            'keywords': [],
            'question_type': 'general',
            'entities': []
        }
        
        # Determine domain
        for domain, categories in self.domain_keywords.items():
            domain_score = 0
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword in query_lower:
                        domain_score += 1
                        analysis['keywords'].append(keyword)
            
            if domain_score > 0:
                analysis['domain'] = domain
                break
        
        # Determine question type
        if any(word in query_lower for word in ['what', 'which', 'how much', 'how many']):
            analysis['question_type'] = 'factual'
        elif any(word in query_lower for word in ['does', 'is', 'are', 'can', 'will']):
            analysis['question_type'] = 'boolean'
        elif any(word in query_lower for word in ['how', 'why', 'when', 'where']):
            analysis['question_type'] = 'explanatory'
        
        # Extract potential entities (numbers, dates, medical terms, etc.)
        analysis['entities'] = self._extract_entities(query)
        
        return analysis
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract important entities from query"""
        entities = []
        
        # Extract numbers and percentages
        numbers = re.findall(r'\d+(?:\.\d+)?%?', query)
        entities.extend(numbers)
        
        # Extract potential medical/legal terms (capitalized words)
        terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', query)
        entities.extend(terms)
        
        # Extract quoted terms
        quoted = re.findall(r'"([^"]*)"', query)
        entities.extend(quoted)
        
        return entities
    
    def _calculate_enhanced_score(self, query: str, clause: ClauseMatch, 
                                 query_analysis: Dict[str, Any]) -> float:
        """
        Calculate enhanced relevance score using multiple factors
        
        Args:
            query: Original query
            clause: Clause to score
            query_analysis: Query analysis results
            
        Returns:
            Enhanced relevance score (0-1)
        """
        base_score = clause.relevance_score
        
        # Keyword matching bonus
        keyword_bonus = self._calculate_keyword_bonus(
            query_analysis['keywords'], clause.content
        )
        
        # Entity matching bonus
        entity_bonus = self._calculate_entity_bonus(
            query_analysis['entities'], clause.content
        )
        
        # Domain-specific bonus
        domain_bonus = self._calculate_domain_bonus(
            query_analysis['domain'], clause.content
        )
        
        # Question type alignment bonus
        type_bonus = self._calculate_type_bonus(
            query_analysis['question_type'], clause.content
        )
        
        # Combine scores with weights
        enhanced_score = (
            base_score * 0.4 +
            keyword_bonus * 0.25 +
            entity_bonus * 0.15 +
            domain_bonus * 0.1 +
            type_bonus * 0.1
        )
        
        return min(enhanced_score, 1.0)  # Cap at 1.0
    
    def _calculate_keyword_bonus(self, keywords: List[str], content: str) -> float:
        """Calculate bonus score based on keyword matches"""
        if not keywords:
            return 0.0
        
        content_lower = content.lower()
        matches = sum(1 for keyword in keywords if keyword in content_lower)
        
        return min(matches / len(keywords), 0.5)
    
    def _calculate_entity_bonus(self, entities: List[str], content: str) -> float:
        """Calculate bonus score based on entity matches"""
        if not entities:
            return 0.0
        
        matches = sum(1 for entity in entities if entity.lower() in content.lower())
        
        return min(matches / len(entities) * 0.3, 0.3)
    
    def _calculate_domain_bonus(self, domain: str, content: str) -> float:
        """Calculate bonus score based on domain-specific terms"""
        if domain == 'general':
            return 0.0
        
        domain_terms = []
        if domain in self.domain_keywords:
            for category_terms in self.domain_keywords[domain].values():
                domain_terms.extend(category_terms)
        
        content_lower = content.lower()
        matches = sum(1 for term in domain_terms if term in content_lower)
        
        return min(matches / max(len(domain_terms), 1) * 0.2, 0.2)
    
    def _calculate_type_bonus(self, question_type: str, content: str) -> float:
        """Calculate bonus based on question type alignment"""
        content_lower = content.lower()
        
        type_indicators = {
            'boolean': ['yes', 'no', 'covered', 'not covered', 'eligible', 'applicable'],
            'factual': ['amount', 'period', 'limit', 'percentage', 'days', 'months'],
            'explanatory': ['because', 'due to', 'provided that', 'subject to', 'means']
        }
        
        if question_type in type_indicators:
            indicators = type_indicators[question_type]
            matches = sum(1 for indicator in indicators if indicator in content_lower)
            return min(matches / len(indicators) * 0.1, 0.1)
        
        return 0.0