"""
Test Normative Extractor on real legal document.
"""

import json
from pathlib import Path
from modules.file_reader.service import read_file
from modules.latinizer.service import latinize_text
from modules.text_normalizer.service import normalize_text
from modules.normative_extractor import extract_normative_content


def test_on_real_document(doc_path: str):
    """
    Test normative extractor on a real legal document.
    
    Args:
        doc_path: Path to the document file
    """
    print("="*80)
    print("NORMATIVE EXTRACTOR - REAL DOCUMENT TEST")
    print("="*80)
    print(f"\nDocument: {doc_path}")
    
    # Check if file exists
    if not Path(doc_path).exists():
        print(f"\n❌ ERROR: File not found: {doc_path}")
        print("\nPlease provide the correct path to the document.")
        return
    
    print("\n" + "-"*80)
    print("STEP 1: Reading document...")
    print("-"*80)
    
    # Read file
    file_result = read_file(doc_path)
    if not file_result or not file_result.get('full_text'):
        print("❌ Failed to read document or no full_text field")
        return
    
    text = file_result['full_text']
    print(f"✓ Document read successfully")
    print(f"  Length: {len(text)} characters")
    print(f"  Lines: {text.count(chr(10))}")
    
    print("\n" + "-"*80)
    print("STEP 2: Latinizing text...")
    print("-"*80)
    
    # Latinize
    latinized = latinize_text(text)
    text = latinized['latinized_text']
    print(f"✓ Text latinized")
    
    print("\n" + "-"*80)
    print("STEP 3: Normalizing text...")
    print("-"*80)
    
    # Normalize
    normalized = normalize_text(text)
    text = normalized['normalized_text']
    print(f"✓ Text normalized")
    
    print("\n" + "-"*80)
    print("STEP 4: Extracting normative content...")
    print("-"*80)
    
    # Extract normative content
    result = extract_normative_content(text)
    nc = result['normative_content']
    
    print(f"✓ Normative content extracted")
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"  Obligations:  {len(nc['obligations'])}")
    print(f"  Prohibitions: {len(nc['prohibitions'])}")
    print(f"  Permissions:  {len(nc['permissions'])}")
    print(f"  Definitions:  {len(nc['definitions'])}")
    print(f"  Total:        {result['total_extracted']}")
    print(f"  Time:         {result['processing_time']:.3f}s")
    
    # Show first few examples of each type
    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80)
    
    if nc['obligations']:
        print(f"\n📋 OBLIGATIONS (showing first 5 of {len(nc['obligations'])}):")
        print("-"*80)
        for i, obl in enumerate(nc['obligations'][:5], 1):
            print(f"\n{i}. {obl['modality'].upper()}")
            print(f"   Subject: {obl['subject']}")
            print(f"   Action:  {obl['action']}")
            if obl['object']:
                print(f"   Object:  {obl['object']}")
            if obl['temporal']:
                print(f"   Temporal: {obl['temporal']}")
            print(f"   Source: \"{obl['source_text'][:100]}...\"" if len(obl['source_text']) > 100 else f"   Source: \"{obl['source_text']}\"")
    
    if nc['prohibitions']:
        print(f"\n🚫 PROHIBITIONS (showing first 5 of {len(nc['prohibitions'])}):")
        print("-"*80)
        for i, proh in enumerate(nc['prohibitions'][:5], 1):
            print(f"\n{i}. {proh['modality'].upper()}")
            print(f"   Subject: {proh['subject']}")
            print(f"   Action:  {proh['action']}")
            if proh['object']:
                print(f"   Object:  {proh['object']}")
            print(f"   Source: \"{proh['source_text'][:100]}...\"" if len(proh['source_text']) > 100 else f"   Source: \"{proh['source_text']}\"")
    
    if nc['permissions']:
        print(f"\n✅ PERMISSIONS (showing first 5 of {len(nc['permissions'])}):")
        print("-"*80)
        for i, perm in enumerate(nc['permissions'][:5], 1):
            print(f"\n{i}. {perm['modality'].upper()}")
            print(f"   Subject: {perm['subject']}")
            print(f"   Action:  {perm['action']}")
            if perm['object']:
                print(f"   Object:  {perm['object']}")
            if perm['condition']:
                print(f"   Condition: {perm['condition']}")
            print(f"   Source: \"{perm['source_text'][:100]}...\"" if len(perm['source_text']) > 100 else f"   Source: \"{perm['source_text']}\"")
    
    if nc['definitions']:
        print(f"\n📖 DEFINITIONS (showing first 5 of {len(nc['definitions'])}):")
        print("-"*80)
        for i, defn in enumerate(nc['definitions'][:5], 1):
            print(f"\n{i}. TERM: {defn['term']}")
            print(f"   Definition: {defn['definition']}")
            if defn['scope']:
                print(f"   Scope: {defn['scope']}")
            print(f"   Source: \"{defn['source_text'][:100]}...\"" if len(defn['source_text']) > 100 else f"   Source: \"{defn['source_text']}\"")
    
    # Save results to JSON
    output_file = Path(doc_path).stem + "_normative_extraction.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*80)
    print(f"✓ Results saved to: {output_file}")
    print("="*80 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        doc_path = sys.argv[1]
    else:
        # Default path - user should provide actual path
        print("\nUsage: python test_normative_on_real_doc.py <path_to_document>")
        print("\nExample:")
        print('  python test_normative_on_real_doc.py "D:/POSAO/ZAKON_O_RADU/ZAKON_O_RADU_DOCX/radni_odnosi_0001_000001_export.docx"')
        print("\nOr provide the path when prompted:")
        doc_path = input("\nEnter document path: ").strip('"')
    
    if doc_path:
        test_on_real_document(doc_path)
    else:
        print("\n❌ No document path provided")

# Made with Bob
