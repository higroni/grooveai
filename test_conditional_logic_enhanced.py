# -*- coding: utf-8 -*-
"""
Test script for enhanced Conditional Logic Extractor module.
Tests new detection capabilities: circular conditions and impossible conditions.
"""

import sys
import io

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.conditional_logic_extractor.service import ConditionalLogicExtractor


def test_circular_conditions():
    """Test circular condition detection."""
    print("\n=== Testing Circular Condition Detection ===")
    
    extractor = ConditionalLogicExtractor()
    
    # Test with circular dependency
    text = """
    Ako zaposleni ima pravo na bonus, mora ispuniti uslove.
    Ako zaposleni ispunjava uslove, ima pravo na bonus.
    """
    
    result = extractor.extract(text)
    content = result.content
    
    print(f"\nText: {text.strip()}")
    print(f"Conditions extracted: {len(content.conditions)}")
    print(f"Rules extracted: {len(content.rules)}")
    print(f"Circular conditions detected: {len(content.circular_conditions)}")
    
    for circ in content.circular_conditions:
        print(f"\n  Circular Dependency:")
        print(f"    Condition 1: {circ.condition1}")
        print(f"    Condition 2: {circ.condition2}")
        print(f"    Chain: {' -> '.join(circ.chain)}")
        print(f"    Confidence: {circ.confidence}")


def test_impossible_conditions_logical():
    """Test impossible condition detection - logical contradictions."""
    print("\n=== Testing Impossible Conditions (Logical) ===")
    
    extractor = ConditionalLogicExtractor()
    
    test_texts = [
        "Zaposleni mora raditi i ne sme raditi istovremeno.",
        "Radnik je dužan da prisustvuje ali je zabranjeno prisustvo.",
        "Ako je zaposleni prisutan i ako nije prisutan, ima pravo na naknadu."
    ]
    
    for text in test_texts:
        result = extractor.extract(text)
        content = result.content
        
        print(f"\nText: {text}")
        print(f"Impossible conditions detected: {len(content.impossible_conditions)}")
        
        for imp in content.impossible_conditions:
            print(f"  Type: {imp.contradiction_type}")
            print(f"  Reason: {imp.reason}")
            print(f"  Confidence: {imp.confidence}")


def test_impossible_conditions_temporal():
    """Test impossible condition detection - temporal contradictions."""
    print("\n=== Testing Impossible Conditions (Temporal) ===")
    
    extractor = ConditionalLogicExtractor()
    
    test_texts = [
        "Zaposleni mora podneti zahtev pre nego što ga podnese i nakon što ga podnese.",
        "Radnik treba da dostavi dokument istovremeno pre i nakon roka."
    ]
    
    for text in test_texts:
        result = extractor.extract(text)
        content = result.content
        
        print(f"\nText: {text}")
        print(f"Impossible conditions detected: {len(content.impossible_conditions)}")
        
        for imp in content.impossible_conditions:
            print(f"  Type: {imp.contradiction_type}")
            print(f"  Reason: {imp.reason}")
            print(f"  Confidence: {imp.confidence}")


def test_impossible_conditions_mutual_exclusion():
    """Test impossible condition detection - mutual exclusion."""
    print("\n=== Testing Impossible Conditions (Mutual Exclusion) ===")
    
    extractor = ConditionalLogicExtractor()
    
    text = "Zaposleni mora biti istovremeno na poslu i ne može biti na poslu."
    
    result = extractor.extract(text)
    content = result.content
    
    print(f"\nText: {text}")
    print(f"Impossible conditions detected: {len(content.impossible_conditions)}")
    
    for imp in content.impossible_conditions:
        print(f"  Condition: {imp.condition_text}")
        print(f"  Type: {imp.contradiction_type}")
        print(f"  Reason: {imp.reason}")
        print(f"  Confidence: {imp.confidence}")


def test_full_extraction():
    """Test full extraction with all features."""
    print("\n=== Testing Full Extraction ===")
    
    extractor = ConditionalLogicExtractor()
    
    text = """
    Ako zaposleni ima pravo na bonus, mora ispuniti uslove.
    Ako zaposleni ispunjava uslove, ima pravo na bonus.
    Radnik mora raditi i ne sme raditi istovremeno.
    Ukoliko zaposleni podnese zahtev, tada poslodavac mora odgovoriti u roku od 15 dana.
    Zaposleni može uzeti godišnji odmor osim ako nije u probnom periodu.
    """
    
    result = extractor.extract(text)
    content = result.content
    
    print(f"\nConditions: {len(content.conditions)}")
    print(f"Consequences: {len(content.consequences)}")
    print(f"Exceptions: {len(content.exceptions)}")
    print(f"Rules: {len(content.rules)}")
    print(f"Circular Conditions: {len(content.circular_conditions)}")
    print(f"Impossible Conditions: {len(content.impossible_conditions)}")
    print(f"\nTotal conditional elements: {content.count_total()}")
    print(f"Processing time: {result.processing_time:.4f}s")
    
    # Show details
    if content.circular_conditions:
        print("\nCircular Conditions:")
        for circ in content.circular_conditions:
            print(f"  - {circ.condition1} <-> {circ.condition2}")
    
    if content.impossible_conditions:
        print("\nImpossible Conditions:")
        for imp in content.impossible_conditions:
            print(f"  - {imp.contradiction_type}: {imp.reason}")


if __name__ == "__main__":
    print("=" * 60)
    print("Enhanced Conditional Logic Extractor Test Suite")
    print("=" * 60)
    
    test_circular_conditions()
    test_impossible_conditions_logical()
    test_impossible_conditions_temporal()
    test_impossible_conditions_mutual_exclusion()
    test_full_extraction()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

# Made with Bob
