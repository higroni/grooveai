"""
Service layer for Assertion Extractor module.
Extracts legal assertions from legal unit content.
"""

import sys
import re
import uuid
from typing import List, Tuple
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.assertion_extractor.models import Assertion, ExtractionStats, ExtractionOutput


class AssertionExtractorService:
    """Service for extracting assertions from legal text."""
    
    def __init__(self):
        """Initialize the assertion extractor service."""
        # Serbian sentence ending patterns
        self.sentence_endings = re.compile(r'[.!?]+\s+')
        
        # Legal assertion indicators (Serbian)
        self.assertion_indicators = [
            r'\b(je\s+dužan|je\s+obavezan|mora|treba|može|ima\s+pravo|zabranjeno\s+je)\b',
            r'\b(ne\s+sme|ne\s+može|nije\s+dozvoljen)\b',
            r'\b(utvrđuje\s+se|određuje\s+se|propisuje\s+se)\b',
            r'\b(smatra\s+se|računa\s+se)\b',
        ]
        
        # Compile patterns
        self.assertion_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.assertion_indicators]
    
    def extract_assertions(
        self,
        content: str,
        min_confidence: float = 0.5
    ) -> ExtractionOutput:
        """
        Extract assertions from legal unit content.
        
        Args:
            content: Legal unit content text
            min_confidence: Minimum confidence threshold (0-1)
            
        Returns:
            ExtractionOutput with assertions and statistics
        """
        # Split into sentences
        sentences = self._split_sentences(content)
        
        # Extract assertions from sentences
        assertions = []
        for idx, (sentence, start_pos, end_pos) in enumerate(sentences):
            confidence = self._calculate_confidence(sentence)
            
            if confidence >= min_confidence:
                assertion = Assertion(
                    assertion_id=str(uuid.uuid4()),
                    text=sentence.strip(),
                    confidence=confidence,
                    sentence_index=idx,
                    start_char=start_pos,
                    end_char=end_pos
                )
                assertions.append(assertion)
        
        # Calculate statistics
        stats = self._calculate_stats(assertions, len(sentences))
        
        return ExtractionOutput(
            assertions=assertions,
            stats=stats
        )
    
    def _split_sentences(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Split text into sentences with position tracking.
        
        Args:
            text: Input text
            
        Returns:
            List of tuples (sentence, start_pos, end_pos)
        """
        sentences = []
        current_pos = 0
        
        # Find all sentence boundaries
        for match in self.sentence_endings.finditer(text):
            end_pos = match.end()
            sentence = text[current_pos:end_pos].strip()
            
            if sentence:
                sentences.append((sentence, current_pos, end_pos))
            
            current_pos = end_pos
        
        # Add remaining text as last sentence
        if current_pos < len(text):
            sentence = text[current_pos:].strip()
            if sentence:
                sentences.append((sentence, current_pos, len(text)))
        
        return sentences
    
    def _calculate_confidence(self, sentence: str) -> float:
        """
        Calculate confidence score for a sentence being an assertion.
        
        Args:
            sentence: Sentence text
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence
        confidence = 0.3
        
        # Check for assertion indicators
        matches = 0
        for pattern in self.assertion_patterns:
            if pattern.search(sentence):
                matches += 1
        
        # Increase confidence based on matches
        if matches > 0:
            confidence += 0.3 * min(matches, 2)  # Max +0.6
        
        # Bonus for sentence length (longer sentences more likely to be assertions)
        word_count = len(sentence.split())
        if word_count >= 5:
            confidence += 0.1
        if word_count >= 10:
            confidence += 0.1
        
        # Penalty for very short sentences
        if word_count < 3:
            confidence -= 0.2
        
        # Ensure confidence is in [0, 1]
        return max(0.0, min(1.0, confidence))
    
    def _calculate_stats(self, assertions: List[Assertion], total_sentences: int) -> ExtractionStats:
        """
        Calculate extraction statistics.
        
        Args:
            assertions: List of extracted assertions
            total_sentences: Total number of sentences processed
            
        Returns:
            ExtractionStats object
        """
        if not assertions:
            return ExtractionStats(
                total_assertions=0,
                total_sentences=total_sentences,
                avg_confidence=0.0
            )
        
        avg_confidence = sum(a.confidence for a in assertions) / len(assertions)
        
        return ExtractionStats(
            total_assertions=len(assertions),
            total_sentences=total_sentences,
            avg_confidence=round(avg_confidence, 3)
        )

# Made with Bob
