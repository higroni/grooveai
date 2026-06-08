# -*- coding: utf-8 -*-
"""
Test script for enhanced Procedural Extractor module.
Tests new extraction capabilities: approval authorities, documentation requirements, form requirements.
"""

import sys
import io

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.procedural_extractor.service import ProceduralExtractor


def test_approval_authorities():
    """Test approval authority extraction."""
    print("\n=== Testing Approval Authority Extraction ===")
    
    extractor = ProceduralExtractor()
    
    test_texts = [
        "Zaposleni može preći na drugo radno mesto uz saglasnost poslodavca.",
        "Ugovor se može raskinuti uz odobrenje ministra.",
        "Radnik ima pravo na odsustvo sa odobrenjem direktora.",
        "Poslodavac daje saglasnost za rad kod drugog poslodavca.",
        "Inspektor izdaje dozvolu za rad."
    ]
    
    for text in test_texts:
        authorities = extractor.extract_approval_authorities(text)
        print(f"\nText: {text}")
        for auth in authorities:
            print(f"  Authority: {auth.authority}")
            print(f"  Type: {auth.approval_type}")
            print(f"  Required for: {auth.required_for}")


def test_documentation_requirements():
    """Test documentation requirement extraction."""
    print("\n=== Testing Documentation Requirement Extraction ===")
    
    extractor = ProceduralExtractor()
    
    test_texts = [
        "Zaposleni podnosi dokaz o stručnoj spremi.",
        "Poslodavac dostavlja potvrdu o zaposlenju u roku od 8 dana.",
        "Radnik prilaže uverenje o zdravstvenom stanju.",
        "Uz zahtev se prilaže izveštaj o radu.",
        "Potrebno je dostaviti zapisnik sa sastanka.",
        "Poslodavac je obavezan da dostavi dokument o isplati."
    ]
    
    for text in test_texts:
        requirements = extractor.extract_documentation_requirements(text)
        print(f"\nText: {text}")
        for req in requirements:
            print(f"  Document Type: {req.document_type}")
            print(f"  Required By: {req.required_by}")
            print(f"  Deadline: {req.deadline}")


def test_form_requirements():
    """Test form requirement extraction."""
    print("\n=== Testing Form Requirement Extraction ===")
    
    extractor = ProceduralExtractor()
    
    test_texts = [
        "Zahtev se podnosi na propisanom obrascu.",
        "Zaposleni popunjava obrazac broj 5.",
        "Prijava se podnosi u formi propisanoj pravilnikom.",
        "Ministar propisuje obrazac za podnošenje zahteva.",
        "Obrazac iz stava 1 ovog člana sadrži podatke o radniku."
    ]
    
    for text in test_texts:
        forms = extractor.extract_form_requirements(text)
        print(f"\nText: {text}")
        for form in forms:
            print(f"  Form Name: {form.form_name}")
            print(f"  Purpose: {form.form_purpose}")
            print(f"  Mandatory: {form.mandatory}")
            print(f"  Prescribed By: {form.prescribed_by}")


def test_full_extraction():
    """Test full extraction with all new features."""
    print("\n=== Testing Full Extraction ===")
    
    extractor = ProceduralExtractor()
    
    text = """
    1) Zaposleni podnosi zahtev za godišnji odmor na propisanom obrascu.
    2) Poslodavac dostavlja potvrdu o zaposlenju u roku od 8 dana.
    3) Radnik može preći na drugo radno mesto uz saglasnost poslodavca.
    Uz zahtev se prilaže dokaz o stručnoj spremi.
    Ministar propisuje obrazac za podnošenje zahteva.
    Direktor daje odobrenje za rad prekovremeno.
    """
    
    result = extractor.extract(text)
    content = result.content
    
    print(f"\nSteps: {len(content.steps)}")
    print(f"Actors: {len(content.actors)}")
    print(f"Approval Authorities: {len(content.approval_authorities)}")
    print(f"Documentation Requirements: {len(content.documentation_requirements)}")
    print(f"Form Requirements: {len(content.form_requirements)}")
    print(f"\nTotal procedural elements: {content.count_total()}")
    print(f"Processing time: {result.processing_time:.4f}s")
    
    # Show details
    if content.approval_authorities:
        print("\nApproval Authorities:")
        for auth in content.approval_authorities:
            print(f"  - {auth.authority} ({auth.approval_type})")
    
    if content.documentation_requirements:
        print("\nDocumentation Requirements:")
        for req in content.documentation_requirements:
            print(f"  - {req.document_type} (by: {req.required_by})")
    
    if content.form_requirements:
        print("\nForm Requirements:")
        for form in content.form_requirements:
            print(f"  - {form.form_name} (mandatory: {form.mandatory})")


if __name__ == "__main__":
    print("=" * 60)
    print("Enhanced Procedural Extractor Test Suite")
    print("=" * 60)
    
    test_approval_authorities()
    test_documentation_requirements()
    test_form_requirements()
    test_full_extraction()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

# Made with Bob
