"""
Test script for Normative Extractor module.
"""

from modules.normative_extractor import extract_normative_content
import json


def test_obligations():
    """Test obligation extraction."""
    print("\n" + "="*80)
    print("TEST 1: OBLIGATION EXTRACTION")
    print("="*80)
    
    text = """
    Poslodavac je dužan da isplati zaradu u roku od 30 dana.
    Zaposleni mora prijaviti bolovanje u roku od 3 dana.
    Poslodavac ima obavezu da obezbedi bezbedne uslove rada.
    """
    
    result = extract_normative_content(text)
    obligations = result['normative_content']['obligations']
    
    print(f"\nFound {len(obligations)} obligations:")
    for i, obl in enumerate(obligations, 1):
        print(f"\n{i}. Obligation:")
        print(f"   Subject: {obl['subject']}")
        print(f"   Action: {obl['action']}")
        print(f"   Object: {obl['object']}")
        print(f"   Modality: {obl['modality']}")
        print(f"   Temporal: {obl['temporal']}")
        print(f"   Source: {obl['source_text']}")


def test_prohibitions():
    """Test prohibition extraction."""
    print("\n" + "="*80)
    print("TEST 2: PROHIBITION EXTRACTION")
    print("="*80)
    
    text = """
    Poslodavac ne sme zapošljavati lica mlađa od 18 godina.
    Zabranjeno je diskriminisanje zaposlenih.
    Zaposleni ne može raditi više od 40 sati nedeljno.
    """
    
    result = extract_normative_content(text)
    prohibitions = result['normative_content']['prohibitions']
    
    print(f"\nFound {len(prohibitions)} prohibitions:")
    for i, proh in enumerate(prohibitions, 1):
        print(f"\n{i}. Prohibition:")
        print(f"   Subject: {proh['subject']}")
        print(f"   Action: {proh['action']}")
        print(f"   Object: {proh['object']}")
        print(f"   Modality: {proh['modality']}")
        print(f"   Source: {proh['source_text']}")


def test_permissions():
    """Test permission extraction."""
    print("\n" + "="*80)
    print("TEST 3: PERMISSION EXTRACTION")
    print("="*80)
    
    text = """
    Zaposleni može raditi noćni rad ako ima pisanu saglasnost.
    Poslodavac ima pravo da otkaže ugovor uz obrazloženje.
    Dozvoljeno je prekovremeno radno vreme u izuzetnim slučajevima.
    """
    
    result = extract_normative_content(text)
    permissions = result['normative_content']['permissions']
    
    print(f"\nFound {len(permissions)} permissions:")
    for i, perm in enumerate(permissions, 1):
        print(f"\n{i}. Permission:")
        print(f"   Subject: {perm['subject']}")
        print(f"   Action: {perm['action']}")
        print(f"   Object: {perm['object']}")
        print(f"   Modality: {perm['modality']}")
        print(f"   Condition: {perm['condition']}")
        print(f"   Source: {perm['source_text']}")


def test_definitions():
    """Test definition extraction."""
    print("\n" + "="*80)
    print("TEST 4: DEFINITION EXTRACTION")
    print("="*80)
    
    text = """
    Zaposleni se smatra fizičko lice koje je u radnom odnosu u smislu ovog zakona.
    U smislu ovog zakona, poslodavac je pravno ili fizičko lice koje zasniva radni odnos.
    Pod terminom "radni odnos" podrazumeva se odnos zasnovan ugovorom o radu.
    """
    
    result = extract_normative_content(text)
    definitions = result['normative_content']['definitions']
    
    print(f"\nFound {len(definitions)} definitions:")
    for i, defn in enumerate(definitions, 1):
        print(f"\n{i}. Definition:")
        print(f"   Term: {defn['term']}")
        print(f"   Definition: {defn['definition']}")
        print(f"   Scope: {defn['scope']}")
        print(f"   Source: {defn['source_text']}")


def test_complex_text():
    """Test with complex legal text."""
    print("\n" + "="*80)
    print("TEST 5: COMPLEX LEGAL TEXT")
    print("="*80)
    
    text = """
    Član 110
    
    Zarada se isplaćuje u rokovima utvrđenim opštim aktom i ugovorom o radu, 
    najmanje jedanput mesečno, a najkasnije do kraja tekućeg meseca za prethodni mesec.
    
    Poslodavac je dužan da isplati zaradu u roku od 30 dana od dana dospeća.
    
    Zabranjeno je isplaćivanje zarade u naturi.
    
    Zaposleni ima pravo na uvid u obračun zarade.
    
    U smislu ovog zakona, zarada je novčani iznos koji zaposleni prima za obavljeni rad.
    """
    
    result = extract_normative_content(text)
    nc = result['normative_content']
    
    print(f"\nExtraction Summary:")
    print(f"  Obligations: {len(nc['obligations'])}")
    print(f"  Prohibitions: {len(nc['prohibitions'])}")
    print(f"  Permissions: {len(nc['permissions'])}")
    print(f"  Definitions: {len(nc['definitions'])}")
    print(f"  Total: {result['total_extracted']}")
    print(f"  Processing time: {result['processing_time']:.3f}s")
    
    print("\n" + "-"*80)
    print("DETAILED RESULTS:")
    print("-"*80)
    
    if nc['obligations']:
        print("\nOBLIGATIONS:")
        for i, obl in enumerate(nc['obligations'], 1):
            print(f"  {i}. {obl['subject']} {obl['modality']} {obl['action']} {obl['object'] or ''}")
            if obl['temporal']:
                print(f"     Temporal: {obl['temporal']}")
    
    if nc['prohibitions']:
        print("\nPROHIBITIONS:")
        for i, proh in enumerate(nc['prohibitions'], 1):
            print(f"  {i}. {proh['subject']} {proh['modality']} {proh['action']} {proh['object'] or ''}")
    
    if nc['permissions']:
        print("\nPERMISSIONS:")
        for i, perm in enumerate(nc['permissions'], 1):
            print(f"  {i}. {perm['subject']} {perm['modality']} {perm['action']} {perm['object'] or ''}")
    
    if nc['definitions']:
        print("\nDEFINITIONS:")
        for i, defn in enumerate(nc['definitions'], 1):
            print(f"  {i}. {defn['term']}: {defn['definition']}")


def test_json_output():
    """Test JSON output format."""
    print("\n" + "="*80)
    print("TEST 6: JSON OUTPUT FORMAT")
    print("="*80)
    
    text = """
    Poslodavac je dužan da isplati zaradu u roku od 30 dana.
    Zabranjeno je diskriminisanje zaposlenih.
    """
    
    result = extract_normative_content(text)
    
    print("\nJSON Output:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("\n" + "="*80)
    print("NORMATIVE EXTRACTOR - TEST SUITE")
    print("="*80)
    
    test_obligations()
    test_prohibitions()
    test_permissions()
    test_definitions()
    test_complex_text()
    test_json_output()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80 + "\n")

# Made with Bob
