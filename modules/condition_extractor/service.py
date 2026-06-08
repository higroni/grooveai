"""
Service layer for condition extraction from legal assertions.
Extracts conditions, exceptions, temporal and modal clauses.
"""
import re
import uuid
from typing import List, Tuple, Dict, Any
from datetime import datetime

from .models import (
    Assertion,
    ExtractedCondition,
    ConditionExtractionRequest,
    ConditionExtractionOutput
)


class ConditionExtractorService:
    """Service for extracting conditions from legal assertions."""
    
    # Condition patterns (ako, kada, u slučaju da, pod uslovom da, u skladu sa)
    CONDITION_PATTERNS = {
        "sr": [
            (r'\bako\b', "ako", 0.9),
            (r'\bkada\b', "kada", 0.85),
            (r'\bu\s+slu[cč]aju\s+da\b', "u slučaju da", 0.9),
            (r'\bpod\s+uslovom\s+da\b', "pod uslovom da", 0.9),
            (r'\bu\s+skladu\s+sa\b', "u skladu sa", 0.9),
            (r'\bukoliko\b', "ukoliko", 0.85),
            (r'\bu\s+slu[cč]aju\s+kada\b', "u slučaju kada", 0.85),
            (r'\bkad\b', "kad", 0.8),
        ],
        "en": [
            (r'\bif\b', "if", 0.9),
            (r'\bwhen\b', "when", 0.85),
            (r'\bin\s+case\b', "in case", 0.9),
            (r'\bprovided\s+that\b', "provided that", 0.9),
            (r'\bin\s+accordance\s+with\b', "in accordance with", 0.9),
            (r'\bunless\b', "unless", 0.85),
        ]
    }
    
    # Exception patterns (osim, izuzev, sem, nije određeno)
    EXCEPTION_PATTERNS = {
        "sr": [
            (r'\bosim\s+ako\b', "osim ako", 0.95),
            (r'\bizuzev\s+u\s+slu[cč]aju\b', "izuzev u slučaju", 0.95),
            (r'\bsem\s+ako\b', "sem ako", 0.9),
            (r'\bsem\s+u\s+slu[cč]aju\b', "sem u slučaju", 0.9),
            (r'\bnije\s+druk[cč]ije\s+odre[đd]eno\b', "nije drukčije određeno", 0.95),
            (r'\bnije\s+odre[đd]eno\b', "nije određeno", 0.9),
            (r'\bosim\b', "osim", 0.85),
            (r'\bizuzev\b', "izuzev", 0.85),
            (r'\bsem\b', "sem", 0.8),
        ],
        "en": [
            (r'\bexcept\s+if\b', "except if", 0.95),
            (r'\bexcept\s+when\b', "except when", 0.95),
            (r'\bunless\s+otherwise\s+provided\b', "unless otherwise provided", 0.95),
            (r'\bunless\s+otherwise\s+specified\b', "unless otherwise specified", 0.95),
            (r'\bexcept\b', "except", 0.85),
            (r'\bexcluding\b', "excluding", 0.8),
            (r'\bother\s+than\b', "other than", 0.8),
        ]
    }
    
    # Temporal patterns (pre, nakon, do, od - only in temporal context)
    TEMPORAL_PATTERNS = {
        "sr": [
            (r'\bu\s+roku\s+od\b', "u roku od", 0.9),
            (r'\bpre\s+(?:nego\s+što|isteka?)\b', "pre nego što", 0.9),
            (r'\bnakon\s+(?:što|isteka?)\b', "nakon što", 0.9),
            (r'\bdo\s+(?:isteka?|momenta?)\b', "do isteka", 0.85),
            (r'\bod\s+(?:momenta?|dana|isteka)\b', "od momenta", 0.85),
            (r'\bpre\s+\d', "pre", 0.8),  # Only before numbers
            (r'\bnakon\s+\d', "nakon", 0.8),  # Only before numbers
            (r'\bdo\s+\d', "do", 0.75),  # Only before numbers
        ],
        "en": [
            (r'\bwithin\b', "within", 0.9),
            (r'\bprior\s+to\b', "prior to", 0.9),
            (r'\bbefore\b', "before", 0.85),
            (r'\bafter\b', "after", 0.85),
            (r'\buntil\b', "until", 0.85),
            (r'\bfrom\b', "from", 0.75),
        ]
    }
    
    # Modal patterns (može, mora, treba, sme, ne može, ne sme)
    MODAL_PATTERNS = {
        "sr": [
            (r'\bne\s+sme\b', "ne sme", 0.95),
            (r'\bne\s+mo[zž]e\b', "ne može", 0.95),
            (r'\bdu[zž]an\s+je\b', "dužan je", 0.95),
            (r'\bobavezan\s+je\b', "obavezan je", 0.95),
            (r'\bmora\b', "mora", 0.95),
            (r'\bmo[zž]e\b', "može", 0.9),
            (r'\btreba\b', "treba", 0.9),
            (r'\bsme\b', "sme", 0.9),
            (r'\bima\s+pravo\b', "ima pravo", 0.9),
            (r'\bne\s+mo[zž]e\s+da\b', "ne može da", 0.95),
        ],
        "en": [
            (r'\bmust\s+not\b', "must not", 0.95),
            (r'\bmay\s+not\b', "may not", 0.95),
            (r'\bis\s+required\s+to\b', "is required to", 0.95),
            (r'\bmust\b', "must", 0.95),
            (r'\bshall\b', "shall", 0.95),
            (r'\bmay\b', "may", 0.9),
            (r'\bshould\b', "should", 0.85),
            (r'\bis\s+entitled\s+to\b', "is entitled to", 0.9),
        ]
    }
    
    def __init__(self):
        """Initialize the condition extractor service."""
        pass
    
    def extract_conditions(self, request: ConditionExtractionRequest) -> ConditionExtractionOutput:
        """
        Extract conditions from an assertion.
        
        Args:
            request: Condition extraction request
            
        Returns:
            ConditionExtractionOutput with extracted conditions
        """
        start_time = datetime.utcnow()
        
        assertion = request.assertion
        language = request.language
        min_confidence = request.min_confidence
        
        all_conditions: List[ExtractedCondition] = []
        
        # Extract different types of conditions
        if request.extract_conditions:
            conditions = self._extract_by_patterns(
                assertion.text,
                self.CONDITION_PATTERNS.get(language, self.CONDITION_PATTERNS["sr"]),
                "condition",
                assertion.assertion_id
            )
            all_conditions.extend([c for c in conditions if c.confidence >= min_confidence])
        
        if request.extract_exceptions:
            exceptions = self._extract_by_patterns(
                assertion.text,
                self.EXCEPTION_PATTERNS.get(language, self.EXCEPTION_PATTERNS["sr"]),
                "exception",
                assertion.assertion_id
            )
            all_conditions.extend([c for c in exceptions if c.confidence >= min_confidence])
        
        if request.extract_temporal:
            temporal = self._extract_by_patterns(
                assertion.text,
                self.TEMPORAL_PATTERNS.get(language, self.TEMPORAL_PATTERNS["sr"]),
                "temporal",
                assertion.assertion_id
            )
            all_conditions.extend([c for c in temporal if c.confidence >= min_confidence])
        
        if request.extract_modal:
            modal = self._extract_by_patterns(
                assertion.text,
                self.MODAL_PATTERNS.get(language, self.MODAL_PATTERNS["sr"]),
                "modal",
                assertion.assertion_id
            )
            all_conditions.extend([c for c in modal if c.confidence >= min_confidence])
        
        # Calculate statistics
        total_conditions = len([c for c in all_conditions if c.condition_type == "condition"])
        total_exceptions = len([c for c in all_conditions if c.condition_type == "exception"])
        total_temporal = len([c for c in all_conditions if c.condition_type == "temporal"])
        total_modal = len([c for c in all_conditions if c.condition_type == "modal"])
        
        avg_confidence = sum(c.confidence for c in all_conditions) / len(all_conditions) if all_conditions else 0.0
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return ConditionExtractionOutput(
            conditions=all_conditions,
            total_conditions=total_conditions,
            total_exceptions=total_exceptions,
            total_temporal=total_temporal,
            total_modal=total_modal,
            average_confidence=round(avg_confidence, 2),
            processing_time_ms=round(processing_time, 2)
        )
    
    def _extract_by_patterns(
        self,
        text: str,
        patterns: List[Tuple[str, str, float]],
        condition_type: str,
        assertion_id: str
    ) -> List[ExtractedCondition]:
        """
        Extract conditions using regex patterns.
        
        Args:
            text: Text to search
            patterns: List of (pattern, trigger_word, confidence) tuples
            condition_type: Type of condition
            assertion_id: Assertion identifier
            
        Returns:
            List of extracted conditions
        """
        conditions = []
        
        for pattern, trigger_word, base_confidence in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start_char = match.start()
                end_char = match.end()
                
                # Extract context (50 chars before and after)
                context_start = max(0, start_char - 50)
                context_end = min(len(text), end_char + 50)
                context = text[context_start:context_end]
                
                # Extract the clause (extend to sentence boundaries)
                clause_text = self._extract_clause(text, start_char, end_char)
                
                condition = ExtractedCondition(
                    condition_id=str(uuid.uuid4()),
                    condition_type=condition_type,
                    text=clause_text,
                    start_char=start_char,
                    end_char=end_char,
                    confidence=base_confidence,
                    trigger_word=trigger_word,
                    context=context
                )
                
                conditions.append(condition)
        
        return conditions
    
    def _extract_clause(self, text: str, start: int, end: int) -> str:
        """
        Extract the full clause containing the matched pattern.
        Extends to sentence boundaries (., ;, :) or clause boundaries (,).
        
        Args:
            text: Full text
            start: Match start position
            end: Match end position
            
        Returns:
            Extracted clause text
        """
        # Find start of clause (look back for sentence/clause boundary)
        clause_start = start
        for i in range(start - 1, max(0, start - 200), -1):
            if text[i] in '.;:\n':
                clause_start = i + 1
                break
            elif text[i] == ',' and i < start - 10:  # Only break on comma if far enough
                clause_start = i + 1
                break
        
        # Find end of clause (look forward for sentence/clause boundary)
        clause_end = end
        for i in range(end, min(len(text), end + 200)):
            if text[i] in '.;:\n':
                clause_end = i
                break
            elif text[i] == ',' and i > end + 10:  # Only break on comma if far enough
                clause_end = i
                break
        
        clause = text[clause_start:clause_end].strip()
        return clause


# Create singleton instance
_service = ConditionExtractorService()


# Wrapper function for easy import
def extract_conditions(assertions: List[Dict[str, Any]], language: str = "sr") -> Dict[str, Any]:
    """
    Wrapper function to extract conditions using the singleton service.
    
    Args:
        assertions: List of assertion dictionaries
        language: Language code (sr or en)
        
    Returns:
        Dictionary with conditions and statistics
    """
    all_conditions = []
    
    # Process each assertion
    for assertion_dict in assertions:
        # Convert dict to Assertion object
        assertion_obj = Assertion(**assertion_dict)
        
        # Create request
        request = ConditionExtractionRequest(
            assertion=assertion_obj,
            language=language
        )
        
        # Extract conditions
        result = _service.extract_conditions(request)
        all_conditions.extend(result.conditions)
    
    return {
        'conditions': [c.dict() for c in all_conditions],
        'total_conditions': len(all_conditions)
    }

# Made with Bob
