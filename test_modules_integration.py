"""
Test integration between Module 1 (File Reader) and Module 2 (Text Normalizer)
"""
import requests
import json

print("=" * 80)
print("TESTING MODULE INTEGRATION")
print("=" * 80)

# Sample PDF file
file_path = "D:/POSAO/OllamaProjects/GROOVE.AI/DOCUMENTS/DEV/onedoc/radni_odnosi_0001_000001.pdf"

# Step 1: Read file with Module 1
print("\nStep 1: Reading PDF with Module 1 (File Reader)...")
print(f"File: {file_path}")

response1 = requests.post("http://localhost:8101/api/read", json={
    "file_path": file_path,
    "file_type": "pdf"
})

if response1.status_code == 200:
    data1 = response1.json()
    extracted_text = data1["output"]["text"]
    
    print(f"Status: SUCCESS")
    print(f"Job ID: {data1['job_id']}")
    print(f"Extracted: {data1['output']['char_count']} characters")
    print(f"Pages: {data1['output']['page_count']}")
    print(f"Processing time: {data1['metadata']['processing_time_ms']} ms")
    
    # Step 2: Normalize text with Module 2
    print("\n" + "-" * 80)
    print("Step 2: Normalizing text with Module 2 (Text Normalizer)...")
    
    response2 = requests.post("http://localhost:8102/api/normalize", json={
        "text": extracted_text,
        "options": {
            "remove_extra_whitespace": True,
            "normalize_newlines": True,
            "fix_encoding": True
        }
    })
    
    if response2.status_code == 200:
        data2 = response2.json()
        normalized_text = data2["output"]["normalized_text"]
        
        print(f"Status: SUCCESS")
        print(f"Job ID: {data2['job_id']}")
        print(f"Changes made: {', '.join(data2['output']['changes_made'])}")
        print(f"Original length: {data2['metadata']['original_length']} chars")
        print(f"Normalized length: {data2['metadata']['normalized_length']} chars")
        print(f"Reduction: {data2['metadata']['original_length'] - data2['metadata']['normalized_length']} chars")
        print(f"Processing time: {data2['metadata']['processing_time_ms']} ms")
        
        # Save results
        with open("integration_test_normalized.txt", "w", encoding="utf-8") as f:
            f.write(normalized_text)
        
        print("\n" + "=" * 80)
        print("INTEGRATION TEST PASSED")
        print("=" * 80)
        print("\nResults:")
        print(f"  - Module 1 extracted {data1['output']['char_count']} characters")
        print(f"  - Module 2 normalized to {data2['metadata']['normalized_length']} characters")
        print(f"  - Total processing time: {data1['metadata']['processing_time_ms'] + data2['metadata']['processing_time_ms']} ms")
        print(f"  - Output saved to: integration_test_normalized.txt")
        
    else:
        print(f"ERROR in Module 2: {response2.status_code}")
        print(response2.text)
else:
    print(f"ERROR in Module 1: {response1.status_code}")
    print(response1.text)

# Made with Bob
