"""
Service for classifying assertions into types.
Types: obligation, prohibition, permission, deadline, definition
"""

import re
from typing import Dict, List, Tuple, Any
from modules.assertion_classifier.models import (
    Assertion,
    ClassificationResult,
    ClassificationOutput
)


# Classification patterns for Serbian language
# Format: (regex_pattern, pattern_name, confidence_score)

OBLIGATION_PATTERNS = {
    "sr": [
        (r'\bmora\b', "mora", 0.95),
        (r'\bdu[žz]an\s+je\b', "dužan je", 0.95),
        (r'\bobavezan\s+je\b', "obavezan je", 0.95),
        (r'\bpotrebno\s+je\b', "potrebno je", 0.85),
        (r'\bneophodna?\s+je\b', "neophodna je", 0.85),
        (r'\bima\s+obavezu\b', "ima obavezu", 0.9),
        (r'\btre[bš]a\b', "treba", 0.8),
        (r'\bdu[žz]nost\b', "dužnost", 0.85),
        (r'\bobaveza\b', "obaveza", 0.85),
    ]
}

PROHIBITION_PATTERNS = {
    "sr": [
        (r'\bne\s+sme\b', "ne sme", 0.95),
        (r'\bne\s+mo[žz]e\b', "ne može", 0.9),
        (r'\bzabranjeno\b', "zabranjeno", 0.95),
        (r'\bne\s+dozvoljava\s+se\b', "ne dozvoljava se", 0.9),
        (r'\bne\s+dopu[šs]ta\s+se\b', "ne dopušta se", 0.9),
        (r'\bne\s+sme\s+se\b', "ne sme se", 0.95),
        (r'\bne\s+mo[žz]e\s+se\b', "ne može se", 0.9),
        (r'\bzabrana\b', "zabrana", 0.85),
        (r'\bisk[lj]u[čc]eno\b', "isključeno", 0.8),
    ]
}

PERMISSION_PATTERNS = {
    "sr": [
        (r'\bmo[žz]e\b', "može", 0.85),
        (r'\bima\s+pravo\b', "ima pravo", 0.95),
        (r'\bdozvoljeno\b', "dozvoljeno", 0.95),
        (r'\bslobodno\b', "slobodno", 0.85),
        (r'\bmo[žz]e\s+se\b', "može se", 0.85),
        (r'\bdopu[šs]teno\b', "dopušteno", 0.9),
        (r'\bovla[šs][ćc]en\b', "ovlašćen", 0.9),
        (r'\bpravo\s+na\b', "pravo na", 0.85),
    ]
}

DEADLINE_PATTERNS = {
    "sr": [
        (r'\bu\s+roku\s+od\b', "u roku od", 0.95),
        (r'\bnajkasnije\s+do\b', "najkasnije do", 0.95),
        (r'\bpre\s+(?:isteka|roka)\b', "pre isteka", 0.9),
        (r'\bdo\s+(?:\d+\s+dana?|kraja)\b', "do X dana", 0.9),
        (r'\bu\s+roku\b', "u roku", 0.85),
        (r'\brok\s+od\b', "rok od", 0.9),
        (r'\bu\s+periodu\b', "u periodu", 0.8),
        (r'\bza\s+vreme\b', "za vreme", 0.75),
        (r'\btokom\b', "tokom", 0.7),
    ]
}

DEFINITION_PATTERNS = {
    "sr": [
        (r'\bjeste\b', "jeste", 0.85),
        (r'\bsmatra\s+se\b', "smatra se", 0.95),
        (r'\bpredstavlja\b', "predstavlja", 0.9),
        (r'\bpodrazumeva\b', "podrazumeva", 0.9),
        (r'\bozna[čc]ava\b', "označava", 0.9),
        (r'\bdefini[šs]e\s+se\b', "definiše se", 0.95),
        (r'\bpod\s+pojmom\b', "pod pojmom", 0.9),
        (r'\bu\s+smislu\s+ovog\b', "u smislu ovog", 0.85),
        (r'\bpod\s+(?:tim|ovim)\s+se\s+podrazumeva\b', "pod tim se podrazumeva", 0.95),
    ]
}


class AssertionClassifierService:
    """Service for classifying assertions into types."""
    
    def __init__(self):
        """Initialize the classifier service."""
        self.patterns = {
            "obligation": OBLIGATION_PATTERNS,
            "prohibition": PROHIBITION_PATTERNS,
            "permission": PERMISSION_PATTERNS,
            "deadline": DEADLINE_PATTERNS,
            "definition": DEFINITION_PATTERNS
        }
    
    def classify_assertion(
        self,
        assertion: Assertion,
        language: str = "sr",
        min_confidence: float = 0.5
    ) -> ClassificationOutput:
        """
        Classify an assertion into one of the types.
        
        Args:
            assertion: Assertion to classify
            language: Language code (default: "sr")
            min_confidence: Minimum confidence threshold
            
        Returns:
            ClassificationOutput with classification result and stats
        """
        text = assertion.text.lower()
        
        # Collect all matches across all types
        all_matches: Dict[str, List[Tuple[str, float]]] = {
            "obligation": [],
            "prohibition": [],
            "permission": [],
            "deadline": [],
            "definition": []
        }
        
        # Check each type
        for assertion_type, pattern_dict in self.patterns.items():
            if language not in pattern_dict:
                continue
                
            patterns = pattern_dict[language]
            for pattern, name, confidence in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    all_matches[assertion_type].append((name, confidence))
        
        # Determine the best type based on highest confidence
        best_type = None
        best_confidence = 0.0
        best_patterns = []
        
        for assertion_type, matches in all_matches.items():
            if matches:
                # Calculate average confidence for this type
                avg_conf = sum(conf for _, conf in matches) / len(matches)
                if avg_conf > best_confidence:
                    best_confidence = avg_conf
                    best_type = assertion_type
                    best_patterns = [name for name, _ in matches]
        
        # If no type found or confidence too low, classify as "obligation" (default)
        if best_type is None or best_confidence < min_confidence:
            best_type = "obligation"
            best_confidence = 0.5
            best_patterns = ["default"]
            reasoning = "No clear pattern matched, defaulting to obligation"
        else:
            reasoning = f"Matched {len(best_patterns)} pattern(s) for {best_type}"
        
        # Create classification result
        classification = ClassificationResult(
            assertion_id=assertion.assertion_id,
            assertion_type=best_type,
            confidence=round(best_confidence, 2),
            matched_patterns=best_patterns,
            reasoning=reasoning
        )
        
        # Create stats
        stats = {
            "total_patterns_checked": sum(len(self.patterns[t].get(language, [])) for t in self.patterns),
            "patterns_matched": sum(len(matches) for matches in all_matches.values()),
            "type_scores": {
                t: round(sum(c for _, c in m) / len(m), 2) if m else 0.0
                for t, m in all_matches.items()
            }
        }
        
        return ClassificationOutput(
            classification=classification,
            stats=stats
        )
    
    def classify_batch(
        self,
        assertions: List[Assertion],
        language: str = "sr",
        min_confidence: float = 0.5
    ) -> List[ClassificationOutput]:
        """
        Classify multiple assertions.
        
        Args:
            assertions: List of assertions to classify
            language: Language code
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of classification outputs
        """
        return [
            self.classify_assertion(assertion, language, min_confidence)
            for assertion in assertions
        ]
    
    def get_pattern_stats(self, language: str = "sr") -> Dict:
        """
        Get statistics about available patterns.
        
        Args:
            language: Language code
            
        Returns:
            Dictionary with pattern statistics
        """
        stats = {}
        for assertion_type, pattern_dict in self.patterns.items():
            if language in pattern_dict:
                patterns = pattern_dict[language]
                stats[assertion_type] = {
                    "count": len(patterns),
                    "avg_confidence": round(sum(c for _, _, c in patterns) / len(patterns), 2),
                    "patterns": [name for _, name, _ in patterns]
                }
        return stats


# Create singleton instance
_service = AssertionClassifierService()


# Wrapper function for easy import
def classify_assertions(assertions: List[Dict[str, Any]], language: str = "sr") -> Dict[str, Any]:
    """
    Wrapper function to classify assertions using the singleton service.
    
    Args:
        assertions: List of assertion dictionaries
        language: Language code (sr or en)
        
    Returns:
        Dictionary with classified assertions
    """
    classified = []
    
    # Process each assertion
    for assertion_dict in assertions:
        # Convert dict to Assertion object
        assertion_obj = Assertion(**assertion_dict)
        
        # Classify assertion
        result = _service.classify_assertion(assertion_obj, language)
        
        # Add classification to assertion dict
        classified_assertion = assertion_dict.copy()
        classified_assertion['classification'] = result.classification.dict() if result.classification else None
        classified.append(classified_assertion)
    
    return {
        'classified_assertions': classified,
        'total_classified': len(classified)
    }

# Made with Bob
