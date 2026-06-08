"""
Test script for Legal Hierarchy Classifier module.
"""

import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.legal_hierarchy import classify_document

# Test cases
test_cases = [
    {
        "name": "Zakon o radu",
        "text": """
ZAKON O RADU

Na osnovu člana 98. Ustava Republike Srbije, Narodna skupština Republike Srbije donosi

ZAKON O RADU

I OSNOVNE ODREDBE

Član 1.

Ovim zakonom uređuju se prava, obaveze i odgovornosti iz radnog odnosa.

U smislu ovog zakona, zaposleni je fizičko lice koje je u radnom odnosu kod poslodavca.

Službeni glasnik RS, br. 24/2005, 61/2005, 54/2009.
"""
    },
    {
        "name": "Pravilnik o bezbednosti",
        "text": """
PRAVILNIK O BEZBEDNOSTI I ZDRAVLJU NA RADU

Na osnovu člana 15. stav 3. Zakona o bezbednosti i zdravlju na radu, 
Ministar rada donosi

PRAVILNIK

Član 1.

Ovim pravilnikom propisuju se mere bezbednosti i zdravlja na radu.

U smislu ovog pravilnika, poslodavac je dužan da obezbedi bezbedne uslove rada.
"""
    },
    {
        "name": "Uredba Vlade",
        "text": """
UREDBA O NAKNADAMA TROŠKOVA

Na osnovu člana 43. stav 2. Zakona o državnoj upravi,
Vlada donosi

UREDBU

Član 1.

Ovom uredbom uređuje se visina naknada troškova za službena putovanja.

Ova uredba stupa na snagu osmog dana od dana objavljivanja u Službenom glasniku.
"""
    },
    {
        "name": "Odluka o organizaciji",
        "text": """
ODLUKA O ORGANIZACIJI RADA

Direktor donosi

ODLUKU

Član 1.

Ovom odlukom uređuje se organizacija rada u preduzeću.

Ova odluka stupa na snagu danom donošenja.
"""
    }
]

def main():
    print("=" * 80)
    print("LEGAL HIERARCHY CLASSIFIER TEST")
    print("=" * 80)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[TEST {i}] {test_case['name']}")
        print("-" * 80)
        
        result = classify_document(test_case['text'])
        results.append({
            "test_name": test_case['name'],
            "result": result
        })
        
        doc = result['document']
        
        print(f"Document Type: {doc['document_type']}")
        print(f"Hierarchy Level: {doc['hierarchy_level']}")
        print(f"Confidence: {doc['confidence']:.2f}")
        
        if doc['issuing_authority']:
            print(f"Issuing Authority: {doc['issuing_authority']}")
        
        if doc['legal_basis']:
            print(f"Legal Basis: {', '.join(doc['legal_basis'][:2])}")
        
        if doc['official_gazette']:
            print(f"Official Gazette: {doc['official_gazette']}")
        
        if result.get('title'):
            print(f"Title: {result['title']}")
        
        print(f"Can Override: {', '.join(doc['can_override'])}")
        print(f"Cannot Override: {', '.join(doc['cannot_override'])}")
        
        if result.get('detected_patterns'):
            print(f"Detected Patterns: {len(result['detected_patterns'])} patterns")
        
        print(f"Processing Time: {result['processing_time']:.4f}s")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    type_counts = {}
    total_time = 0
    
    for item in results:
        doc_type = item['result']['document']['document_type']
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        total_time += item['result']['processing_time']
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Total Processing Time: {total_time:.4f}s")
    print(f"Average Time per Document: {total_time/len(results):.4f}s")
    
    print("\nDocument Types Detected:")
    for doc_type, count in sorted(type_counts.items()):
        print(f"  - {doc_type}: {count}")
    
    # Save results
    output_file = "legal_hierarchy_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()

# Made with Bob
