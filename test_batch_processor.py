"""
Test script for batch processor with a small set of documents.
Tests the complete M1-M9 pipeline with direct function calls.
"""

import sys
from pathlib import Path
from batch_processor import BatchProcessor

def main():
    """Test batch processor with sample documents."""
    
    # Find test documents
    test_docs_dir = Path("test_data/documents")
    
    if not test_docs_dir.exists():
        print(f"Error: Test documents directory not found: {test_docs_dir}")
        print("Please create test_data/documents/ and add some PDF files")
        sys.exit(1)
    
    # Get all PDF files
    pdf_files = list(test_docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"Error: No PDF files found in {test_docs_dir}")
        sys.exit(1)
    
    # Limit to first 3 documents for initial test
    test_files = [str(f) for f in pdf_files[:3]]
    
    print("="*80)
    print("BATCH PROCESSOR TEST")
    print("="*80)
    print(f"Test documents: {len(test_files)}")
    for f in test_files:
        print(f"  - {Path(f).name}")
    print()
    
    # Create batch processor with 2 workers for testing
    processor = BatchProcessor(
        num_workers=2,
        batch_size=10,
        unified_db_path="data/databases/grooveai_unified.db"
    )
    
    # Process documents
    print("Starting batch processing...")
    print()
    
    stats = processor.process_documents(
        document_paths=test_files
    )
    
    # Print detailed results
    print()
    print("="*80)
    print("DETAILED RESULTS")
    print("="*80)
    
    for result in stats['results']:
        print(f"\n{result['document']}:")
        print(f"  Processing time: {result['processing_time']:.2f}s")
        print(f"  Legal units: {result.get('legal_units_count', 0)}")
        print(f"  Assertions: {result.get('assertions_count', 0)}")
        print(f"  Entities: {result.get('entities_count', 0)}")
        print(f"  Conditions: {result.get('conditions_count', 0)}")
    
    if stats['failures']:
        print("\nFAILED DOCUMENTS:")
        for failure in stats['failures']:
            print(f"  {failure['document']}: {failure['error']}")
    
    print()
    print("="*80)
    print("Test complete!")
    print("="*80)

if __name__ == "__main__":
    main()

# Made with Bob
