import json
import sys

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Load the processed JSON
with open('test_output/single_doc_test/radni_odnosi_0001_000001_processed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== DOCUMENT METADATA ===")
print(json.dumps(data['document_metadata'], indent=2, ensure_ascii=False))

print("\n=== DOCUMENT LEVEL ===")
print(f"document_legal_unit_id: {data.get('document_legal_unit_id')}")

print("\n=== FIRST UNIT (parent_legal_unit_id check) ===")
if data.get('parsed_structure', {}).get('units'):
    unit = data['parsed_structure']['units'][0]
    print(f"unit_id: {unit.get('unit_id')}")
    print(f"parent_legal_unit_id: {unit.get('parent_legal_unit_id')}")
    print(f"document_legal_unit_id: {unit.get('document_legal_unit_id')}")
    
    # Check if parent_legal_unit_id matches document_legal_unit_id
    if unit.get('parent_legal_unit_id') == data.get('document_legal_unit_id'):
        print("\n✓ parent_legal_unit_id correctly set to document_legal_unit_id!")
    else:
        print("\n✗ parent_legal_unit_id does NOT match document_legal_unit_id")

print("\n=== CHECKING processed_at ===")
if 'processed_at' in data['document_metadata']:
    print(f"✓ processed_at found in document_metadata: {data['document_metadata']['processed_at']}")
else:
    print("✗ processed_at NOT found in document_metadata")

# Made with Bob
