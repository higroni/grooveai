# -*- coding: utf-8 -*-
"""
Test script for enhanced Normative Extractor module.
Tests new extraction capabilities: waivers, transfers, assignments, ambiguity, circular definitions.
"""

import sys
import io

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.normative_extractor.service import NormativeExtractor

def test_waivers():
    """Test waiver extraction."""
    print("\n=== Testing Waiver Extraction ===")
    
    extractor = NormativeExtractor()
    
    test_texts = [
        "Zaposleni odriče se prava na naknadu štete.",
        "Radnik ne može se odreći prava na godišnji odmor.",
        "Odricanje od prava na penziju je ništavo.",
        "Odricanje od prava na zdravstvenu zaštitu."
    ]
    
    for text in test_texts:
        waivers = extractor.extract_waivers(text)
        print(f"\nText: {text}")
        for waiver in waivers:
            print(f"  Subject: {waiver.subject}")
            print(f"  Right: {waiver.right}")
            print(f"  Waivable: {waiver.waivable}")
            print(f"  Confidence: {waiver.confidence}")


def test_transfers():
    """Test transfer extraction."""
    print("\n=== Testing Transfer Extraction ===")
    
    extractor = NormativeExtractor()
    
    test_texts = [
        "Vlasnik prenosi imovinu na naslednika.",
        "Pravo svojine se prenosi na kupca.",
        "Obaveza plaćanja prelazi na pravnog sledbenika.",
        "Ne može se preneti pravo glasa."
    ]
    
    for text in test_texts:
        transfers = extractor.extract_transfers(text)
        print(f"\nText: {text}")
        for transfer in transfers:
            print(f"  From: {transfer.from_party}")
            print(f"  To: {transfer.to_party}")
            print(f"  Subject: {transfer.subject}")
            print(f"  Transferable: {transfer.transferable}")
            print(f"  Confidence: {transfer.confidence}")


def test_assignments():
    """Test assignment extraction."""
    print("\n=== Testing Assignment Extraction ===")
    
    extractor = NormativeExtractor()
    
    test_texts = [
        "Poverilac ustupa potraživanje trećem licu.",
        "Zakupac može ustupiti zakup uz saglasnost zakupodavca.",
        "Ustupanje prava zahteva saglasnost druge strane.",
        "Ustupanje ugovora je zabranjeno."
    ]
    
    for text in test_texts:
        assignments = extractor.extract_assignments(text)
        print(f"\nText: {text}")
        for assignment in assignments:
            print(f"  Assignor: {assignment.assignor}")
            print(f"  Assignee: {assignment.assignee}")
            print(f"  Subject: {assignment.subject}")
            print(f"  Requires Consent: {assignment.requires_consent}")
            print(f"  Condition: {assignment.condition}")
            print(f"  Confidence: {assignment.confidence}")


def test_ambiguity():
    """Test ambiguity detection."""
    print("\n=== Testing Ambiguity Detection ===")
    
    extractor = NormativeExtractor()
    
    test_texts = [
        "Zaposleni mora preduzeti odgovarajuće mere.",
        "Poslodavac je dužan da obezbedi primeren nivo zaštite.",
        "Radnik ima pravo na razumnu naknadu.",
        "Potrebno je obezbediti dovoljan broj radnika.",
        "Ugovor mora biti jasan i nedvosmislen."  # No vague terms
    ]
    
    for text in test_texts:
        ambiguity_scores = extractor.detect_ambiguity(text)
        print(f"\nText: {text}")
        if ambiguity_scores:
            for score in ambiguity_scores:
                print(f"  Ambiguity Score: {score.ambiguity_score}")
                print(f"  Vague Terms: {score.ambiguous_terms}")
        else:
            print("  No ambiguity detected")


def test_circular_definitions():
    """Test circular definition detection."""
    print("\n=== Testing Circular Definition Detection ===")
    
    extractor = NormativeExtractor()
    
    # First extract definitions
    text = """
    Zaposleni se smatra lice koje obavlja poslove u smislu ovog zakona.
    Poslovi se smatraju aktivnosti koje obavlja zaposleni u smislu ovog zakona.
    Radnik je zaposleni koji obavlja fizičke poslove.
    """
    
    definitions = extractor.extract_definitions(text)
    print(f"\nExtracted {len(definitions)} definitions:")
    for d in definitions:
        print(f"  {d.term}: {d.definition}")
    
    # Detect circular references
    circular_defs = extractor.detect_circular_definitions(definitions)
    print(f"\nDetected {len(circular_defs)} circular definitions:")
    for circ in circular_defs:
        print(f"  {circ.term1} <-> {circ.term2}")
        print(f"  Confidence: {circ.confidence}")


def test_full_extraction():
    """Test full extraction with all new features."""
    print("\n=== Testing Full Extraction ===")
    
    extractor = NormativeExtractor()
    
    text = """
    Zaposleni je dužan da obavlja poslove savesno i odgovorno.
    Zaposleni odriče se prava na naknadu prekovremenog rada.
    Poslodavac prenosi vlasništvo na zaposlenog nakon pet godina.
    Zaposleni može ustupiti pravo na bonus uz saglasnost poslodavca.
    Poslodavac mora obezbediti odgovarajuće uslove rada.
    Zaposleni se smatra lice koje obavlja poslove u smislu ovog zakona.
    Poslovi se smatraju aktivnosti koje obavlja zaposleni.
    """
    
    result = extractor.extract(text)
    content = result.normative_content
    
    print(f"\nObligations: {len(content.obligations)}")
    print(f"Waivers: {len(content.waivers)}")
    print(f"Transfers: {len(content.transfers)}")
    print(f"Assignments: {len(content.assignments)}")
    print(f"Definitions: {len(content.definitions)}")
    print(f"Ambiguity Scores: {len(content.ambiguity_scores)}")
    print(f"Circular Definitions: {len(content.circular_definitions)}")
    print(f"\nTotal normative elements: {content.total_count}")
    print(f"Processing time: {result.processing_time:.4f}s")


if __name__ == "__main__":
    print("=" * 60)
    print("Enhanced Normative Extractor Test Suite")
    print("=" * 60)
    
    test_waivers()
    test_transfers()
    test_assignments()
    test_ambiguity()
    test_circular_definitions()
    test_full_extraction()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

# Made with Bob
