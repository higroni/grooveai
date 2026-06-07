"""
Integration test for Modules 1, 2, 3, 4, 6, 7, 8, and 9.
Tests the complete pipeline: File Reader -> Text Normalizer -> Latinizer -> Legal Parser 
-> Assertion Extractor -> Entity Recognizer -> Condition Extractor -> Assertion Classifier
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
ENTITY_RECOGNIZER_URL = "http://localhost:8107"
CONDITION_EXTRACTOR_URL = "http://localhost:8108"
ASSERTION_CLASSIFIER_URL = "http://localhost:8109"

# Test PDF file from config
TEST_PDF = config.get_sample_file()

def test_full_pipeline():
    """Test the complete pipeline from PDF to classified assertions."""
    
    print("=" * 80)
    print("FULL PIPELINE TEST: Modules 1 -> 2 -> 3 -> 4 -> 6 -> 7 -> 8 -> 9")
    print("File Reader -> Text Normalizer -> Latinizer -> Legal Parser")
    print("-> Assertion Extractor -> Entity Recognizer -> Condition Extractor")
    print("-> Assertion Classifier")
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
    
    # Step 6: Extract assertions from parsed articles
    print("\n[STEP 6] Extracting assertions from articles...")
    
    legal_units = output['legal_units']
    articles = [unit for unit in legal_units if unit['unit_type'] == 'article']
    
    print(f"[INFO] Found {len(articles)} articles to process")
    print(f"[INFO] Processing first 5 articles for demonstration...")
    
    all_assertions = []
    extraction_jobs = []
    
    for i, article in enumerate(articles[:5], 1):
        article_number = article.get('number', 'N/A')
        content = article.get('content_text', '')
        
        if not content or len(content.strip()) < 20:
            print(f"  [{i}/5] Article {article_number}: Skipped (empty or too short)")
            continue
        
        print(f"  [{i}/5] Article {article_number}: Extracting assertions...")
        
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
    
    # Step 7: Extract entities from assertions
    print("\n[STEP 7] Extracting entities from assertions...")
    print(f"[INFO] Processing {len(all_assertions)} assertions...")
    
    all_entities = []
    recognition_jobs = []
    entity_stats = {
        'PERSON': 0,
        'ORGANIZATION': 0,
        'LOCATION': 0,
        'DATE': 0,
        'MONEY': 0,
        'PERCENTAGE': 0,
        'LEGAL_REF': 0,
        'DURATION': 0
    }
    
    for i, assertion in enumerate(all_assertions, 1):
        assertion_text = assertion['text']
        assertion_id = assertion['assertion_id']
        
        print(f"  [{i}/{len(all_assertions)}] Processing assertion {assertion_id[:8]}...")
        
        try:
            response7 = requests.post(
                f"{ENTITY_RECOGNIZER_URL}/api/recognize",
                json={
                    "assertion": {
                        "assertion_id": assertion_id,
                        "text": assertion_text,
                        "confidence": assertion.get('confidence', 0.5)
                    },
                    "language": "sr",
                    "min_confidence": 0.5,
                    "use_ner": False  # Disable NER, use regex only for legal documents
                }
            )
            
            if response7.status_code == 200:
                data7 = response7.json()
                entities = data7['entities']
                stats = data7['stats']
                
                recognition_jobs.append({
                    'job_id': data7['job_id'],
                    'assertion_id': assertion_id,
                    'entities_count': len(entities),
                    'stats': stats
                })
                
                # Update entity type statistics
                for entity in entities:
                    entity_type = entity['entity_type']
                    if entity_type in entity_stats:
                        entity_stats[entity_type] += 1
                
                all_entities.extend(entities)
                
                if len(entities) > 0:
                    print(f"       -> Found {len(entities)} entities (avg confidence: {stats['avg_confidence']:.2f})")
                else:
                    print(f"       -> No entities found")
            else:
                print(f"       -> ERROR: Status {response7.status_code}")
                
        except Exception as e:
            print(f"       -> ERROR: {str(e)}")
    
    print(f"\n[OK] Entity recognition complete!")
    print(f"[OK] Total entities extracted: {len(all_entities)}")
    print(f"[OK] Total recognition jobs: {len(recognition_jobs)}")
    
    # Step 8: Extract conditions from assertions
    print(f"\n[STEP 8] Extracting conditions from assertions...")
    print(f"[INFO] Processing {len(all_assertions)} assertions")
    
    condition_jobs = []
    all_conditions = []
    condition_stats = {
        "condition": 0,
        "exception": 0,
        "temporal": 0,
        "modal": 0
    }
    
    for i, assertion in enumerate(all_assertions[:5], 1):  # Process first 5 assertions for demo
        assertion_id = assertion['assertion_id']
        assertion_text = assertion['text']
        
        print(f"\n  [{i}/{min(5, len(all_assertions))}] Processing assertion: {assertion_id}")
        print(f"       Text: {assertion_text[:100]}...")
        
        try:
            response8 = requests.post(
                f"{CONDITION_EXTRACTOR_URL}/api/extract",
                json={
                    "assertion": {
                        "assertion_id": assertion_id,
                        "text": assertion_text,
                        "confidence": assertion.get('confidence', 0.5)
                    },
                    "language": "sr",
                    "min_confidence": 0.5,
                    "extract_conditions": True,
                    "extract_exceptions": True,
                    "extract_temporal": True,
                    "extract_modal": True
                }
            )
            
            if response8.status_code == 200:
                data8 = response8.json()
                job_id = data8['job_id']
                conditions = data8['output']['conditions']
                
                condition_jobs.append({
                    'job_id': job_id,
                    'assertion_id': assertion_id,
                    'total_conditions': data8['output']['total_conditions'],
                    'total_exceptions': data8['output']['total_exceptions'],
                    'total_temporal': data8['output']['total_temporal'],
                    'total_modal': data8['output']['total_modal']
                })
                
                all_conditions.extend(conditions)
                
                # Update statistics
                condition_stats['condition'] += data8['output']['total_conditions']
                condition_stats['exception'] += data8['output']['total_exceptions']
                condition_stats['temporal'] += data8['output']['total_temporal']
                condition_stats['modal'] += data8['output']['total_modal']
                
                print(f"       -> Extracted {len(conditions)} conditions")
                print(f"          Cond:{data8['output']['total_conditions']} Exc:{data8['output']['total_exceptions']} Temp:{data8['output']['total_temporal']} Modal:{data8['output']['total_modal']}")
            else:
                print(f"       -> ERROR: Status {response8.status_code}")
                
        except Exception as e:
            print(f"       -> ERROR: {str(e)}")
    
    print(f"\n[OK] Condition extraction complete!")
    print(f"[OK] Total conditions extracted: {len(all_conditions)}")
    print(f"[OK] Total condition jobs: {len(condition_jobs)}")
    
    # Step 9: Classify assertions using Module 9
    print(f"\n[STEP 9] Classifying assertions...")
    print(f"[INFO] Processing {len(all_assertions)} assertions")
    
    classification_jobs = []
    all_classifications = []
    classification_stats = {
        "obligation": 0,
        "prohibition": 0,
        "permission": 0,
        "deadline": 0,
        "definition": 0
    }
    
    for i, assertion in enumerate(all_assertions, 1):
        assertion_id = assertion['assertion_id']
        assertion_text = assertion['text']
        
        print(f"  [{i}/{len(all_assertions)}] Classifying assertion {assertion_id[:8]}...")
        
        try:
            response9 = requests.post(
                f"{ASSERTION_CLASSIFIER_URL}/classify",
                json={
                    "assertion": {
                        "assertion_id": assertion_id,
                        "text": assertion_text,
                        "confidence": assertion.get('confidence', 0.5)
                    },
                    "language": "sr",
                    "min_confidence": 0.5
                }
            )
            
            if response9.status_code == 200:
                data9 = response9.json()
                classification = data9['output']['classification']
                
                classification_jobs.append({
                    'job_id': data9['job_id'],
                    'assertion_id': assertion_id,
                    'assertion_type': classification['assertion_type'],
                    'confidence': classification['confidence'],
                    'matched_patterns': classification['matched_patterns']
                })
                
                all_classifications.append(classification)
                
                # Update statistics
                assertion_type = classification['assertion_type']
                if assertion_type in classification_stats:
                    classification_stats[assertion_type] += 1
                
                print(f"       -> Type: {classification['assertion_type']} (confidence: {classification['confidence']:.2f})")
            else:
                print(f"       -> ERROR: Status {response9.status_code}")
                
        except Exception as e:
            print(f"       -> ERROR: {str(e)}")
    
    print(f"\n[OK] Classification complete!")
    print(f"[OK] Total assertions classified: {len(all_classifications)}")
    print(f"[OK] Total classification jobs: {len(classification_jobs)}")
    
    # Display entity statistics
    print("\n[STATISTICS] Entities by type:")
    for entity_type, count in entity_stats.items():
        if count > 0:
            print(f"  - {entity_type}: {count}")
    
    # Display condition statistics
    print("\n[STATISTICS] Conditions by type:")
    for condition_type, count in condition_stats.items():
        if count > 0:
            print(f"  - {condition_type}: {count}")
    
    # Display classification statistics
    print("\n[STATISTICS] Assertions by type:")
    for assertion_type, count in classification_stats.items():
        if count > 0:
            print(f"  - {assertion_type}: {count}")
    
    # Display sample classifications
    print("\n[PREVIEW] Sample classifications (first 10):")
    for i, classification in enumerate(all_classifications[:10], 1):
        print(f"\n  {i}. Type: {classification['assertion_type']}")
        print(f"     Confidence: {classification['confidence']:.2f}")
        print(f"     Patterns: {', '.join(classification['matched_patterns'])}")
        print(f"     Reasoning: {classification['reasoning']}")
    
    # Save complete pipeline output
    output_file = "pipeline_output_complete.json"
    print(f"\n[SAVING] Writing complete pipeline output to {output_file}...")
    
    pipeline_output = {
        "pipeline": "Modules 1 -> 2 -> 3 -> 4 -> 6 -> 7 -> 8 -> 9",
        "source_file": TEST_PDF,
        "jobs": {
            "file_reader": job1_id,
            "text_normalizer": job2_id,
            "latinizer": job3_id,
            "legal_parser": job4_id,
            "assertion_extractor": [job['job_id'] for job in extraction_jobs],
            "entity_recognizer": [job['job_id'] for job in recognition_jobs],
            "condition_extractor": [job['job_id'] for job in condition_jobs],
            "assertion_classifier": [job['job_id'] for job in classification_jobs]
        },
        "statistics": {
            "raw_text_length": len(raw_text),
            "normalized_text_length": len(normalized_text),
            "latinized_text_length": len(latinized_text),
            "cyrillic_converted": data3['cyrillic_chars_converted'],
            "total_legal_units": output['statistics']['total_units'],
            "total_articles": output['statistics']['total_articles'],
            "articles_processed": len(extraction_jobs),
            "total_assertions": len(all_assertions),
            "total_entities": len(all_entities),
            "entities_by_type": entity_stats,
            "total_conditions": len(all_conditions),
            "conditions_by_type": condition_stats,
            "total_classifications": len(all_classifications),
            "classifications_by_type": classification_stats
        },
        "extraction_jobs": extraction_jobs,
        "recognition_jobs": recognition_jobs,
        "condition_jobs": condition_jobs,
        "classification_jobs": classification_jobs,
        "assertions": all_assertions,
        "entities": all_entities,
        "conditions": all_conditions,
        "classifications": all_classifications
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(pipeline_output, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved to {output_file}")
    
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
    print(f"Module 7 (Entity Recognizer):")
    print(f"  - Assertions processed:      {len(recognition_jobs):>10}")
    print(f"  - Entities extracted:        {len(all_entities):>10}")
    if all_entities:
        avg_conf = sum(e['confidence'] for e in all_entities) / len(all_entities)
        print(f"  - Average confidence:        {avg_conf:>10.2f}")
    print(f"\n  Entities by type:")
    for entity_type, count in entity_stats.items():
        if count > 0:
            print(f"    - {entity_type:20} {count:>10}")
    print(f"Module 8 (Condition Extractor):")
    print(f"  - Assertions processed:      {len(condition_jobs):>10}")
    print(f"  - Conditions extracted:      {len(all_conditions):>10}")
    if all_conditions:
        avg_conf = sum(c['confidence'] for c in all_conditions) / len(all_conditions)
        print(f"  - Average confidence:        {avg_conf:>10.2f}")
    print(f"\n  Conditions by type:")
    for condition_type, count in condition_stats.items():
        if count > 0:
            print(f"    - {condition_type:20} {count:>10}")
    print(f"Module 9 (Assertion Classifier):")
    print(f"  - Assertions classified:     {len(all_classifications):>10}")
    if all_classifications:
        avg_conf = sum(c['confidence'] for c in all_classifications) / len(all_classifications)
        print(f"  - Average confidence:        {avg_conf:>10.2f}")
    print(f"\n  Classifications by type:")
    for assertion_type, count in classification_stats.items():
        if count > 0:
            print(f"    - {assertion_type:20} {count:>10}")
    print("=" * 80)
    print(f"\nOutput file: {output_file}")
    print("\nFull pipeline test completed successfully!")

if __name__ == "__main__":
    try:
        test_full_pipeline()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob