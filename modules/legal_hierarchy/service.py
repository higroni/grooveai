"""
Legal Hierarchy Classifier Service - Classifies documents by legal hierarchy.

This module classifies legal documents by their type and hierarchy level
(zakon, pravilnik, uredba, odluka, etc.)
"""

import re
import time
from typing import Optional, List, Dict, Any
from .models import LegalDocument, HierarchyClassificationResult


class LegalHierarchyClassifier:
    """
    Classifies legal documents by hierarchy level.
    """
    
    # Hierarchy levels (1 = highest authority)
    HIERARCHY = {
        "ustav": 1,
        "zakon": 2,
        "uredba": 3,
        "pravilnik": 4,
        "odluka": 5,
        "naređenje": 6
    }
    
    # Document type patterns
    DOCUMENT_TYPE_PATTERNS = {
        "ustav": [
            r'USTAV\s+Republike\s+Srbije',
            r'USTAV\s+Srbije',
        ],
        "zakon": [
            r'ZAKON\s+o\s+[a-zšđčćž\s]+',
            r'Zakon\s+o\s+[a-zšđčćž\s]+',
            r'ovaj\s+zakon',
            r'u\s+smislu\s+ovog\s+zakona',
        ],
        "uredba": [
            r'UREDBA\s+o\s+[a-zšđčćž\s]+',
            r'Uredba\s+o\s+[a-zšđčćž\s]+',
            r'Vlada\s+donosi\s+UREDBU',
            r'ova\s+uredba',
        ],
        "pravilnik": [
            r'PRAVILNIK\s+o\s+[a-zšđčćž\s]+',
            r'Pravilnik\s+o\s+[a-zšđčćž\s]+',
            r'ovaj\s+pravilnik',
            r'u\s+smislu\s+ovog\s+pravilnika',
        ],
        "odluka": [
            r'ODLUKA\s+o\s+[a-zšđčćž\s]+',
            r'Odluka\s+o\s+[a-zšđčćž\s]+',
            r'ova\s+odluka',
            r'donosi\s+ODLUKU',
        ],
        "naređenje": [
            r'NAREĐENJE\s+o\s+[a-zšđčćž\s]+',
            r'Naređenje\s+o\s+[a-zšđčćž\s]+',
            r'ovo\s+naređenje',
        ]
    }
    
    # Issuing authority patterns
    AUTHORITY_PATTERNS = {
        "Narodna skupština": [
            r'Narodna\s+skupština\s+Republike\s+Srbije',
            r'Narodna\s+skupština',
        ],
        "Vlada Republike Srbije": [
            r'Vlada\s+Republike\s+Srbije',
            r'Vlada\s+donosi',
        ],
        "Ministarstvo": [
            r'Ministar\s+[a-zšđčćž\s]+donosi',
            r'Ministarstvo\s+[a-zšđčćž\s]+',
        ],
    }
    
    # Legal basis patterns
    LEGAL_BASIS_PATTERNS = [
        r'Na\s+osnovu\s+člana\s+(\d+)[^,.;!?]+',
        r'Na\s+osnovu\s+([^,.;!?]+Zakona[^,.;!?]+)',
        r'U\s+skladu\s+sa\s+([^,.;!?]+)',
    ]
    
    # Official gazette patterns
    GAZETTE_PATTERNS = [
        r'Službeni\s+glasnik\s+RS[^,.;!?]+',
        r'Službeni\s+list[^,.;!?]+',
    ]
    
    def __init__(self):
        """Initialize the classifier."""
        # Compile patterns for better performance
        self.document_patterns = {
            doc_type: [re.compile(p, re.IGNORECASE) for p in patterns]
            for doc_type, patterns in self.DOCUMENT_TYPE_PATTERNS.items()
        }
        
        self.authority_patterns = {
            authority: [re.compile(p, re.IGNORECASE) for p in patterns]
            for authority, patterns in self.AUTHORITY_PATTERNS.items()
        }
        
        self.legal_basis_patterns = [re.compile(p, re.IGNORECASE) for p in self.LEGAL_BASIS_PATTERNS]
        self.gazette_patterns = [re.compile(p, re.IGNORECASE) for p in self.GAZETTE_PATTERNS]
    
    def classify_document_type(self, text: str) -> tuple[str, List[str], float]:
        """
        Classify document type based on text patterns.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (document_type, matched_patterns, confidence)
        """
        # Count matches for each document type
        type_scores = {}
        matched_patterns = {}
        
        for doc_type, patterns in self.document_patterns.items():
            matches = []
            for pattern in patterns:
                found = pattern.findall(text)
                if found:
                    matches.extend([pattern.pattern for _ in found])
            
            if matches:
                type_scores[doc_type] = len(matches)
                matched_patterns[doc_type] = matches
        
        if not type_scores:
            return "unknown", [], 0.0
        
        # Get type with highest score
        best_type = max(type_scores.items(), key=lambda x: x[1])[0]
        confidence = min(0.9, 0.5 + (type_scores[best_type] * 0.1))
        
        return best_type, matched_patterns.get(best_type, []), confidence
    
    def extract_issuing_authority(self, text: str) -> Optional[str]:
        """
        Extract issuing authority from text.
        
        Args:
            text: Input text
            
        Returns:
            Authority name or None
        """
        for authority, patterns in self.authority_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    return authority
        
        return None
    
    def extract_legal_basis(self, text: str) -> List[str]:
        """
        Extract legal basis references from text.
        
        Args:
            text: Input text
            
        Returns:
            List of legal basis references
        """
        basis_list = []
        
        for pattern in self.legal_basis_patterns:
            matches = pattern.findall(text)
            basis_list.extend(matches)
        
        return basis_list[:5]  # Limit to first 5
    
    def extract_official_gazette(self, text: str) -> Optional[str]:
        """
        Extract official gazette reference from text.
        
        Args:
            text: Input text
            
        Returns:
            Gazette reference or None
        """
        for pattern in self.gazette_patterns:
            match = pattern.search(text)
            if match:
                return match.group(0)
        
        return None
    
    def extract_title(self, text: str) -> Optional[str]:
        """
        Extract document title from text.
        
        Args:
            text: Input text
            
        Returns:
            Document title or None
        """
        # Look for title patterns at the beginning
        title_patterns = [
            r'^([A-ZŠĐČĆŽ][A-ZŠĐČĆŽ\s]+)\s*\n',  # All caps title
            r'(ZAKON|UREDBA|PRAVILNIK|ODLUKA|NAREĐENJE)\s+o\s+([a-zšđčćž\s]+)',
        ]
        
        for pattern_str in title_patterns:
            pattern = re.compile(pattern_str, re.MULTILINE | re.IGNORECASE)
            match = pattern.search(text[:500])  # Search in first 500 chars
            if match:
                return match.group(0).strip()
        
        return None
    
    def get_hierarchy_relationships(self, doc_type: str) -> tuple[List[str], List[str]]:
        """
        Get what this document type can and cannot override.
        
        Args:
            doc_type: Document type
            
        Returns:
            Tuple of (can_override, cannot_override)
        """
        level = self.HIERARCHY.get(doc_type, 999)
        
        can_override = [
            dtype for dtype, dlevel in self.HIERARCHY.items()
            if dlevel > level
        ]
        
        cannot_override = [
            dtype for dtype, dlevel in self.HIERARCHY.items()
            if dlevel <= level and dtype != doc_type
        ]
        
        return can_override, cannot_override
    
    def classify(self, text: str) -> HierarchyClassificationResult:
        """
        Classify document hierarchy.
        
        Args:
            text: Input text
            
        Returns:
            HierarchyClassificationResult
        """
        start_time = time.time()
        
        # Classify document type
        doc_type, matched_patterns, confidence = self.classify_document_type(text)
        
        # Extract metadata
        authority = self.extract_issuing_authority(text)
        legal_basis = self.extract_legal_basis(text)
        gazette = self.extract_official_gazette(text)
        title = self.extract_title(text)
        
        # Get hierarchy relationships
        can_override, cannot_override = self.get_hierarchy_relationships(doc_type)
        
        # Build legal document
        document = LegalDocument(
            document_type=doc_type,
            hierarchy_level=self.HIERARCHY.get(doc_type, 999),
            issuing_authority=authority,
            legal_basis=legal_basis,
            official_gazette=gazette,
            can_override=can_override,
            cannot_override=cannot_override,
            confidence=confidence
        )
        
        processing_time = time.time() - start_time
        
        return HierarchyClassificationResult(
            document=document,
            title=title,
            detected_patterns=matched_patterns,
            processing_time=processing_time
        )


# Singleton instance
_classifier = None

def get_classifier() -> LegalHierarchyClassifier:
    """Get singleton classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = LegalHierarchyClassifier()
    return _classifier


def classify_document(text: str) -> Dict[str, Any]:
    """
    Classify document hierarchy.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with classification result
    """
    classifier = get_classifier()
    result = classifier.classify(text)
    return result.to_dict()

# Made with Bob
