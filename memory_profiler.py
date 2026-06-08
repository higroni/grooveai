"""
Memory profiler for batch processor - identifies memory leaks
"""

import os
import gc
import sys
import tracemalloc
import psutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.file_reader.service import FileReaderService
from modules.latinizer.service import LatinizerService
from modules.text_normalizer.service import TextNormalizerService
from modules.legal_parser.service import LegalParserService
from modules.entity_recognizer.service import EntityRecognizerService
from modules.assertion_extractor.service import AssertionExtractorService
from modules.condition_extractor.service import ConditionExtractorService
from modules.assertion_classifier.service import AssertionClassifierService


def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


def profile_single_document(doc_path: str):
    """Profile memory usage for a single document"""
    
    print(f"\n{'='*80}")
    print(f"PROFILING: {os.path.basename(doc_path)}")
    print(f"{'='*80}\n")
    
    # Start memory tracking
    tracemalloc.start()
    initial_memory = get_memory_usage()
    print(f"Initial memory: {initial_memory:.2f} MB")
    
    # Initialize services
    print("\n1. Initializing services...")
    mem_before = get_memory_usage()
    
    file_reader = FileReaderService()
    latinizer = LatinizerService()
    normalizer = TextNormalizerService()
    parser = LegalParserService()
    entity_recognizer = EntityRecognizerService()
    assertion_extractor = AssertionExtractorService()
    condition_extractor = ConditionExtractorService()
    classifier = AssertionClassifierService()
    
    mem_after = get_memory_usage()
    print(f"   Memory after init: {mem_after:.2f} MB (+{mem_after - mem_before:.2f} MB)")
    
    # M1: File Reader
    print("\n2. M1: File Reader...")
    mem_before = get_memory_usage()
    snapshot_before = tracemalloc.take_snapshot()
    
    file_data = file_reader.read_file(doc_path)
    
    mem_after = get_memory_usage()
    snapshot_after = tracemalloc.take_snapshot()
    print(f"   Memory: {mem_after:.2f} MB (+{mem_after - mem_before:.2f} MB)")
    print(f"   Text length: {len(file_data.get('text', ''))} chars")
    
    # Show top memory allocations
    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    print("   Top 3 memory allocations:")
    for stat in top_stats[:3]:
        print(f"      {stat}")
    
    # M2: Latinizer
    print("\n3. M2: Latinizer...")
    mem_before = get_memory_usage()
    snapshot_before = tracemalloc.take_snapshot()
    
    latin_result = latinizer.latinize_text(file_data['text'])
    latinized_text = latin_result['latinized_text']
    
    mem_after = get_memory_usage()
    snapshot_after = tracemalloc.take_snapshot()
    print(f"   Memory: {mem_after:.2f} MB (+{mem_after - mem_before:.2f} MB)")
    
    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    print("   Top 3 memory allocations:")
    for stat in top_stats[:3]:
        print(f"      {stat}")
    
    # Cleanup M1 data
    del file_data
    gc.collect()
    mem_after_gc = get_memory_usage()
    print(f"   After cleanup: {mem_after_gc:.2f} MB (freed {mem_after - mem_after_gc:.2f} MB)")
    
    # M3: Normalizer
    print("\n4. M3: Text Normalizer...")
    mem_before = get_memory_usage()
    snapshot_before = tracemalloc.take_snapshot()
    
    norm_result = normalizer.normalize_text(latinized_text)
    normalized_text = norm_result['normalized_text']
    
    mem_after = get_memory_usage()
    snapshot_after = tracemalloc.take_snapshot()
    print(f"   Memory: {mem_after:.2f} MB (+{mem_after - mem_before:.2f} MB)")
    
    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    print("   Top 3 memory allocations:")
    for stat in top_stats[:3]:
        print(f"      {stat}")
    
    # Cleanup M2 data
    del latin_result, latinized_text
    gc.collect()
    mem_after_gc = get_memory_usage()
    print(f"   After cleanup: {mem_after_gc:.2f} MB (freed {mem_after - mem_after_gc:.2f} MB)")
    
    # M4: Parser
    print("\n5. M4: Legal Parser...")
    mem_before = get_memory_usage()
    snapshot_before = tracemalloc.take_snapshot()
    
    parse_output = parser.parse_document(
        text=normalized_text,
        source_uri=doc_path,
        filename=os.path.basename(doc_path)
    )
    
    mem_after = get_memory_usage()
    snapshot_after = tracemalloc.take_snapshot()
    print(f"   Memory: {mem_after:.2f} MB (+{mem_after - mem_before:.2f} MB)")
    print(f"   Legal units: {len(parse_output.legal_units)}")
    
    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    print("   Top 3 memory allocations:")
    for stat in top_stats[:3]:
        print(f"      {stat}")
    
    # M6: Entity Recognizer
    print("\n6. M6: Entity Recognizer...")
    mem_before = get_memory_usage()
    snapshot_before = tracemalloc.take_snapshot()
    
    # Document level
    full_doc_entities = entity_recognizer.recognize_entities(normalized_text)
    
    # Unit level
    unit_level_entities = []
    for unit in parse_output.legal_units:
        if unit.content:
            entities = entity_recognizer.recognize_entities(unit.content)
            unit_level_entities.extend(entities)
    
    mem_after = get_memory_usage()
    snapshot_after = tracemalloc.take_snapshot()
    print(f"   Memory: {mem_after:.2f} MB (+{mem_after - mem_before:.2f} MB)")
    print(f"   Entities: {len(full_doc_entities)} doc + {len(unit_level_entities)} units")
    
    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    print("   Top 3 memory allocations:")
    for stat in top_stats[:3]:
        print(f"      {stat}")
    
    # Cleanup M3 data
    del norm_result, normalized_text
    gc.collect()
    mem_after_gc = get_memory_usage()
    print(f"   After cleanup: {mem_after_gc:.2f} MB (freed {mem_after - mem_after_gc:.2f} MB)")
    
    # M7: Assertion Extractor
    print("\n7. M7: Assertion Extractor...")
    mem_before = get_memory_usage()
    snapshot_before = tracemalloc.take_snapshot()
    
    all_assertions = []
    for unit in parse_output.legal_units:
        if unit.content:
            assertions = assertion_extractor.extract_assertions(unit.content)
            all_assertions.extend(assertions)
    
    mem_after = get_memory_usage()
    snapshot_after = tracemalloc.take_snapshot()
    print(f"   Memory: {mem_after:.2f} MB (+{mem_after - mem_before:.2f} MB)")
    print(f"   Assertions: {len(all_assertions)}")
    
    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    print("   Top 3 memory allocations:")
    for stat in top_stats[:3]:
        print(f"      {stat}")
    
    # M8: Condition Extractor
    print("\n8. M8: Condition Extractor...")
    mem_before = get_memory_usage()
    snapshot_before = tracemalloc.take_snapshot()
    
    conditions = []
    for assertion in all_assertions:
        cond = condition_extractor.extract_conditions(assertion['text'])
        if cond:
            conditions.append(cond)
    
    mem_after = get_memory_usage()
    snapshot_after = tracemalloc.take_snapshot()
    print(f"   Memory: {mem_after:.2f} MB (+{mem_after - mem_before:.2f} MB)")
    print(f"   Conditions: {len(conditions)}")
    
    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    print("   Top 3 memory allocations:")
    for stat in top_stats[:3]:
        print(f"      {stat}")
    
    # M9: Classifier
    print("\n9. M9: Assertion Classifier...")
    mem_before = get_memory_usage()
    snapshot_before = tracemalloc.take_snapshot()
    
    classified = []
    for assertion in all_assertions:
        result = classifier.classify_assertion(assertion['text'])
        classified.append(result)
    
    mem_after = get_memory_usage()
    snapshot_after = tracemalloc.take_snapshot()
    print(f"   Memory: {mem_after:.2f} MB (+{mem_after - mem_before:.2f} MB)")
    
    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    print("   Top 3 memory allocations:")
    for stat in top_stats[:3]:
        print(f"      {stat}")
    
    # Final cleanup
    print("\n10. Final cleanup...")
    mem_before = get_memory_usage()
    
    del parse_output, full_doc_entities, unit_level_entities
    del all_assertions, conditions, classified
    del file_reader, latinizer, normalizer, parser
    del entity_recognizer, assertion_extractor, condition_extractor, classifier
    
    gc.collect()
    gc.collect()  # Second pass
    
    mem_after = get_memory_usage()
    print(f"   Memory before cleanup: {mem_before:.2f} MB")
    print(f"   Memory after cleanup: {mem_after:.2f} MB")
    print(f"   Freed: {mem_before - mem_after:.2f} MB")
    
    # Stop tracking
    tracemalloc.stop()
    
    final_memory = get_memory_usage()
    total_leaked = final_memory - initial_memory
    
    print(f"\n{'='*80}")
    print(f"SUMMARY:")
    print(f"  Initial memory: {initial_memory:.2f} MB")
    print(f"  Final memory: {final_memory:.2f} MB")
    print(f"  LEAKED: {total_leaked:.2f} MB")
    print(f"{'='*80}\n")
    
    return total_leaked


def profile_multiple_documents(doc_dir: str, num_docs: int = 5):
    """Profile memory usage across multiple documents"""
    
    print(f"\n{'#'*80}")
    print(f"MULTI-DOCUMENT PROFILING: {num_docs} documents")
    print(f"{'#'*80}\n")
    
    doc_files = sorted(Path(doc_dir).glob("*.pdf"))[:num_docs]
    
    initial_memory = get_memory_usage()
    leaked_per_doc = []
    
    for i, doc_path in enumerate(doc_files, 1):
        print(f"\n[{i}/{num_docs}] Processing document...")
        leaked = profile_single_document(str(doc_path))
        leaked_per_doc.append(leaked)
        
        current_memory = get_memory_usage()
        cumulative_leak = current_memory - initial_memory
        
        print(f"\nCUMULATIVE STATS after {i} documents:")
        print(f"  Total leaked: {cumulative_leak:.2f} MB")
        print(f"  Average per doc: {cumulative_leak / i:.2f} MB")
        print(f"  Current memory: {current_memory:.2f} MB")
        
        if cumulative_leak > 1000:  # Stop if > 1GB leaked
            print("\n⚠️  WARNING: Memory leak > 1GB, stopping profiling")
            break
    
    print(f"\n{'#'*80}")
    print(f"FINAL SUMMARY:")
    print(f"  Documents processed: {len(leaked_per_doc)}")
    print(f"  Total leaked: {sum(leaked_per_doc):.2f} MB")
    print(f"  Average per doc: {sum(leaked_per_doc) / len(leaked_per_doc):.2f} MB")
    print(f"  Estimated for 100 docs: {(sum(leaked_per_doc) / len(leaked_per_doc)) * 100:.2f} MB")
    print(f"{'#'*80}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Profile memory usage")
    parser.add_argument("--doc", help="Single document to profile")
    parser.add_argument("--dir", default="test_data/documents2", help="Directory with documents")
    parser.add_argument("--num", type=int, default=5, help="Number of documents to profile")
    
    args = parser.parse_args()
    
    if args.doc:
        profile_single_document(args.doc)
    else:
        profile_multiple_documents(args.dir, args.num)

# Made with Bob
