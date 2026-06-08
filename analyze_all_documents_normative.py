"""
Analyze all documents for normative content extraction.
Exports results to single JSON file for analysis.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any
from modules.file_reader.service import read_file
from modules.latinizer.service import latinize_text
from modules.text_normalizer.service import normalize_text
from modules.normative_extractor import extract_normative_content


def process_document(doc_path: Path) -> Dict[str, Any]:
    """
    Process a single document and extract normative content.
    
    Args:
        doc_path: Path to document
        
    Returns:
        Dictionary with document analysis
    """
    doc_id = doc_path.stem
    
    try:
        # Read document
        file_result = read_file(str(doc_path))
        if not file_result or not file_result.get('full_text'):
            return {
                'doc_id': doc_id,
                'status': 'error',
                'error': 'Failed to read document or no full_text',
                'pure_text': None,
                'extracted': None
            }
        
        # Get pure text
        pure_text = file_result['full_text']
        
        # Latinize
        latinized = latinize_text(pure_text)
        text = latinized['latinized_text']
        
        # Normalize
        normalized = normalize_text(text)
        text = normalized['normalized_text']
        
        # Extract normative content
        result = extract_normative_content(text)
        
        return {
            'doc_id': doc_id,
            'status': 'success',
            'pure_text': pure_text[:500] + '...' if len(pure_text) > 500 else pure_text,  # First 500 chars
            'text_length': len(pure_text),
            'extracted': {
                'obligations': result['normative_content']['obligations'],
                'prohibitions': result['normative_content']['prohibitions'],
                'permissions': result['normative_content']['permissions'],
                'definitions': result['normative_content']['definitions'],
                'total_count': result['total_extracted']
            },
            'processing_time': result['processing_time']
        }
        
    except Exception as e:
        return {
            'doc_id': doc_id,
            'status': 'error',
            'error': str(e),
            'pure_text': None,
            'extracted': None
        }


def analyze_all_documents(input_dir: str, output_file: str = 'normative_analysis_all.json'):
    """
    Analyze all documents in directory and export to JSON.
    
    Args:
        input_dir: Directory containing documents
        output_file: Output JSON file path
    """
    input_path = Path(input_dir)
    
    # Get all document files
    doc_files = sorted([
        f for f in input_path.glob("*")
        if f.suffix.lower() in ['.docx', '.pdf', '.txt']
    ])
    
    if not doc_files:
        print(f"❌ No documents found in {input_dir}")
        return
    
    total_docs = len(doc_files)
    
    print("="*80)
    print("NORMATIVE CONTENT ANALYSIS - ALL DOCUMENTS")
    print("="*80)
    print(f"Total documents: {total_docs}")
    print(f"Output file: {output_file}")
    print("="*80 + "\n")
    
    results = []
    start_time = time.time()
    
    # Process each document
    for i, doc_file in enumerate(doc_files, 1):
        print(f"[{i}/{total_docs}] Processing: {doc_file.name}...", end=' ')
        
        doc_result = process_document(doc_file)
        results.append(doc_result)
        
        if doc_result['status'] == 'success':
            extracted = doc_result['extracted']
            print(f"✓ (O:{len(extracted['obligations'])} P:{len(extracted['prohibitions'])} "
                  f"Pe:{len(extracted['permissions'])} D:{len(extracted['definitions'])})")
        else:
            print(f"✗ {doc_result['error']}")
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = total_docs - successful
    
    total_obligations = sum(len(r['extracted']['obligations']) for r in results if r['status'] == 'success')
    total_prohibitions = sum(len(r['extracted']['prohibitions']) for r in results if r['status'] == 'success')
    total_permissions = sum(len(r['extracted']['permissions']) for r in results if r['status'] == 'success')
    total_definitions = sum(len(r['extracted']['definitions']) for r in results if r['status'] == 'success')
    total_extracted = total_obligations + total_prohibitions + total_permissions + total_definitions
    
    # Build final output
    output = {
        'metadata': {
            'total_documents': total_docs,
            'successful': successful,
            'failed': failed,
            'processing_time': total_time,
            'avg_time_per_doc': total_time / total_docs if total_docs > 0 else 0
        },
        'statistics': {
            'total_obligations': total_obligations,
            'total_prohibitions': total_prohibitions,
            'total_permissions': total_permissions,
            'total_definitions': total_definitions,
            'total_extracted': total_extracted,
            'avg_per_document': total_extracted / successful if successful > 0 else 0
        },
        'documents': results
    }
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"Total documents:     {total_docs}")
    print(f"Successful:          {successful}")
    print(f"Failed:              {failed}")
    print(f"Total time:          {total_time:.1f}s")
    print(f"Avg time per doc:    {total_time/total_docs:.2f}s")
    print("\n" + "-"*80)
    print("EXTRACTED CONTENT:")
    print("-"*80)
    print(f"Obligations:         {total_obligations}")
    print(f"Prohibitions:        {total_prohibitions}")
    print(f"Permissions:         {total_permissions}")
    print(f"Definitions:         {total_definitions}")
    print(f"Total:               {total_extracted}")
    print(f"Avg per document:    {total_extracted/successful:.1f}" if successful > 0 else "N/A")
    print("="*80)
    print(f"\n✓ Results saved to: {output_file}")
    print("\nYou can now analyze the results to improve regex patterns.")
    print("="*80 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'normative_analysis_all.json'
    else:
        print("\nUsage: python analyze_all_documents_normative.py <input_dir> [output_file]")
        print("\nExample:")
        print('  python analyze_all_documents_normative.py "D:/POSAO/ZAKON_O_RADU/ZAKON_O_RADU_DOCX"')
        print('  python analyze_all_documents_normative.py "D:/POSAO/ZAKON_O_RADU/ZAKON_O_RADU_DOCX" results.json')
        print("\nOr provide the path when prompted:")
        input_dir = input("Enter input directory: ").strip('"')
        output_file = input("Enter output file (default: normative_analysis_all.json): ").strip() or 'normative_analysis_all.json'
    
    if input_dir:
        analyze_all_documents(input_dir, output_file)
    else:
        print("\n❌ No input directory provided")

# Made with Bob
