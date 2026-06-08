import json

with open('radni_odnosi_0001_000001_export.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"Import Run ID: {data['import_run_id']}")
print(f"Document: {data['document'].get('name', 'N/A')}")
print(f"Full text length: {len(data['full_text'])} chars")
print(f"Total assertions: {len(data['assertions'])}")

if data['assertions']:
    print(f"\nFirst assertion:")
    first = data['assertions'][0]
    print(f"  ID: {first.get('assertion_id', 'N/A')}")
    print(f"  Text: {first.get('text', 'N/A')[:100]}...")
    print(f"  Entities: {len(first.get('entities', []))}")
    print(f"  Conditions: {len(first.get('conditions', []))}")
    print(f"  Classification: {first.get('classification', {})}")

# Made with Bob
