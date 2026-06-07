"""
Integration test for Modules 1, 2, 3, 4, and 6.
Tests the complete pipeline: File Reader -> Text Normalizer -> Latinizer -> Legal Parser -> Assertion Extractor
"""

import requests
import json
import time
import sys
import io
from shared.config_loader import config

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Module URLs
FILE_READER_URL = "http://localhost:8101"
TEXT_NORMALIZER_URL = "http://localhost:8102"
LATINIZER_URL = "http://localhost:8103"
LEGAL_PARSER_URL = "http://localhost:8105"
ASSERTION_EXTRACTOR_URL = "http://localhost:8106"

# Test PDF file from config
TEST_PDF = config.get_sample_file()

def test_full_pipeline():
    """Test the complete pipeline from PDF to extracted assertions."""
    
    print("=" * 80)
    print("FULL PIPELINE TEST: Modules 1 -> 2 -> 3 -> 4 -> 6")
    print("File Reader -> Text Normalizer -> Latinizer -> Legal Parser -> Assertion Extractor")
    print("=" * 80)
    
    # Step 1: Read PDF file
    print("\n[STEP 1] Reading PDF file...")
    print(f"File: {TEST_PDF}")
    
    response1 = requests.post(
        f"{FILE_READER_URL}/api/read",
        json={"file_path": TEST_PDF}
    )
    
    if response1.status_code not in [200, 201]:
        print(f"ERROR: File Reader failed with status {response1.status_code}")
        return
    
    data1 = response1.json()
    job1_id = data1["job_id"]
    raw_text = data1["output"]["text"]
    
    print(f"[OK] Job ID: {job1_id}")
    print(f"[OK] Extracted {len(raw_text)} characters")
    print(f"[OK] Processing time: {data1['metadata']['processing_time_ms']}ms")
    
    # Step 2: Normalize text
    print("\n[STEP 2] Normalizing text...")
    
    response2 = requests.post(
        f"{TEXT_NORMALIZER_URL}/api/normalize",
        json={"text": raw_text}
    )
    
    if response2.status_code not in [200, 201]:
        print(f"ERROR: Text Normalizer failed with status {response2.status_code}")
        return
    
    data2 = response2.json()
    job2_id = data2["job_id"]
    normalized_text = data2["output"]["normalized_text"]
    
    print(f"[OK] Job ID: {job2_id}")
    print(f"[OK] Normalized {len(normalized_text)} characters")
    print(f"[OK] Processing time: {data2['metadata']['processing_time_ms']}ms")
    
    # Step 3: Latinize text
    print("\n[STEP 3] Latinizing text (Cyrillic -> Latin)...")
    
    response3 = requests.post(
        f"{LATINIZER_URL}/api/latinize",
        json={"text": normalized_text}
    )
    
    if response3.status_code not in [200, 201]:
        print(f"ERROR: Latinizer failed with status {response3.status_code}")
        return
    
    data3 = response3.json()
    job3_id = data3["job_id"]
    latinized_text = data3["latinized_text"]
    
    print(f"[OK] Job ID: {job3_id}")
    print(f"[OK] Latinized {len(latinized_text)} characters")
    print(f"[OK] Cyrillic chars converted: {data3['cyrillic_chars_converted']}")
    
    # Step 4: Parse legal structure
    print("\n[STEP 4] Parsing legal structure...")
    
    response4 = requests.post(
        f"{LEGAL_PARSER_URL}/api/parse",
        json={
            "text": latinized_text,
            "source_uri": f"file:///{TEST_PDF}",
            "filename": TEST_PDF.split("/")[-1]
        }
    )
    
    if response4.status_code not in [200, 201]:
        print(f"ERROR: Legal Parser failed with status {response4.status_code}")
        print(f"Response: {response4.text}")
        return
    
    data4 = response4.json()
    job4_id = data4["job_id"]
    output = data4["output"]
    
    print(f"[OK] Job ID: {job4_id}")
    print(f"[OK] Document: {output['document']['filename']}")
    print(f"[OK] Total units: {output['statistics']['total_units']}")
    print(f"[OK] Articles: {output['statistics']['total_articles']}")
    
    # Step 5: Extract assertions from parsed articles
    print("\n[STEP 5] Extracting assertions from articles...")
    
    legal_units = output['legal_units']
    articles = [unit for unit in legal_units if unit['unit_type'] == 'article']
    
    print(f"[INFO] Found {len(articles)} articles to process")
    print(f"[INFO] Processing first 10 articles for demonstration...")
    
    all_assertions = []
    extraction_jobs = []
    
    for i, article in enumerate(articles[:10], 1):
        article_number = article.get('number', 'N/A')
        content = article.get('content_text', '')
        
        if not content or len(content.strip()) < 20:
            print(f"  [{i}/10] Article {article_number}: Skipped (empty or too short)")
            continue
        
        print(f"  [{i}/10] Article {article_number}: Extracting assertions...")
        
        try:
            response6 = requests.post(
                f"{ASSERTION_EXTRACTOR_URL}/api/extract",
                json={
                    "legal_unit": {
                        "unit_id": article['legal_unit_id'],
                        "content": content,
                        "unit_type": "article",
                        "number": article_number
                    },
                    "language": "sr",
                    "min_confidence": 0.5
                }
            )
            
            if response6.status_code == 200:
                data6 = response6.json()
                assertions = data6['output']['assertions']
                stats = data6['output']['stats']
                
                extraction_jobs.append({
                    'job_id': data6['job_id'],
                    'article_number': article_number,
                    'article_id': article['legal_unit_id'],
                    'assertions_count': len(assertions),
                    'stats': stats
                })
                
                all_assertions.extend(assertions)
                
                print(f"       -> Found {len(assertions)} assertions (avg confidence: {stats['avg_confidence']:.2f})")
            else:
                print(f"       -> ERROR: Status {response6.status_code}")
                
        except Exception as e:
            print(f"       -> ERROR: {str(e)}")
    
    print(f"\n[OK] Extraction complete!")
    print(f"[OK] Total assertions extracted: {len(all_assertions)}")
    print(f"[OK] Total extraction jobs: {len(extraction_jobs)}")
    
    # Display sample assertions
    print("\n[PREVIEW] Sample assertions (first 5):")
    for i, assertion in enumerate(all_assertions[:5], 1):
        print(f"\n  {i}. {assertion['text']}")
        print(f"     Confidence: {assertion['confidence']:.2f}")
        print(f"     Assertion ID: {assertion['assertion_id']}")
    
    # Save complete pipeline output
    output_file = "pipeline_output_with_assertions.json"
    print(f"\n[SAVING] Writing complete pipeline output to {output_file}...")
    
    pipeline_output = {
        "pipeline": "Modules 1 -> 2 -> 3 -> 4 -> 6",
        "source_file": TEST_PDF,
        "jobs": {
            "file_reader": job1_id,
            "text_normalizer": job2_id,
            "latinizer": job3_id,
            "legal_parser": job4_id,
            "assertion_extractor": [job['job_id'] for job in extraction_jobs]
        },
        "statistics": {
            "raw_text_length": len(raw_text),
            "normalized_text_length": len(normalized_text),
            "latinized_text_length": len(latinized_text),
            "cyrillic_converted": data3['cyrillic_chars_converted'],
            "total_legal_units": output['statistics']['total_units'],
            "total_articles": output['statistics']['total_articles'],
            "articles_processed": len(extraction_jobs),
            "total_assertions": len(all_assertions)
        },
        "extraction_jobs": extraction_jobs,
        "assertions": all_assertions
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(pipeline_output, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved to {output_file}")
    
    # Save assertions as readable text
    output_file_txt = "pipeline_output_assertions.txt"
    print(f"[SAVING] Writing assertions to {output_file_txt}...")
    
    with open(output_file_txt, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("EXTRACTED ASSERTIONS FROM LEGAL DOCUMENT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Source: {TEST_PDF}\n")
        f.write(f"Total Articles Processed: {len(extraction_jobs)}\n")
        f.write(f"Total Assertions Extracted: {len(all_assertions)}\n\n")
        f.write("=" * 80 + "\n\n")
        
        # Group by article
        for job in extraction_jobs:
            article_assertions = [a for a in all_assertions if any(
                e['article_id'] == job['article_id'] 
                for e in extraction_jobs 
                if e['job_id'] == job['job_id']
            )]
            
            f.write(f"ARTICLE {job['article_number']}\n")
            f.write(f"Assertions: {job['assertions_count']}\n")
            f.write(f"Average Confidence: {job['stats']['avg_confidence']:.2f}\n")
            f.write("-" * 80 + "\n\n")
            
            for i, assertion in enumerate(article_assertions, 1):
                f.write(f"{i}. {assertion['text']}\n")
                f.write(f"   Confidence: {assertion['confidence']:.2f}\n")
                f.write(f"   ID: {assertion['assertion_id']}\n\n")
            
            f.write("\n")
    
    print(f"[OK] Saved to {output_file_txt}")
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPLETE PIPELINE SUMMARY")
    print("=" * 80)
    print(f"Module 1 (File Reader):        {len(raw_text):>10} chars")
    print(f"Module 2 (Text Normalizer):    {len(normalized_text):>10} chars")
    print(f"Module 3 (Latinizer):          {len(latinized_text):>10} chars")
    print(f"Module 4 (Legal Parser):       {output['statistics']['total_units']:>10} units")
    print(f"  - Articles:                  {output['statistics']['total_articles']:>10}")
    print(f"  - Paragraphs:                {output['statistics']['total_paragraphs']:>10}")
    print(f"Module 6 (Assertion Extractor):")
    print(f"  - Articles processed:        {len(extraction_jobs):>10}")
    print(f"  - Assertions extracted:      {len(all_assertions):>10}")
    if all_assertions:
        avg_conf = sum(a['confidence'] for a in all_assertions) / len(all_assertions)
        print(f"  - Average confidence:        {avg_conf:>10.2f}")
    print("=" * 80)
    print(f"\nOutput files:")
    print(f"  - {output_file} (complete pipeline JSON)")
    print(f"  - {output_file_txt} (assertions text)")
    print("\nFull pipeline test completed successfully!")

if __name__ == "__main__":
    try:
        test_full_pipeline()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob