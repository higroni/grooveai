"""
Analyze JSON export files for normative content extraction.
Uses already exported JSON files instead of processing original documents.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any
from modules.normative_extractor import extract_normative_content


def process_json_export(json_path: Path) -> Dict[str, Any]:
    """
    Process a single JSON export file and extract normative content.
    
    Args:
        json_path: Path to JSON export file
        
    Returns:
        Dictionary with document analysis
    """
    doc_id = json_path.stem
    
    try:
        # Read JSON export
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get full_text from JSON
        full_text = data.get('full_text', '')
        if not full_text:
            return {
                'doc_id': doc_id,
                'status': 'error',
                'error': 'No full_text in JSON',
                'pure_text': None,
                'extracted': None
            }
        
        # Extract normative content directly from full_text
        # (already latinized and normalized in JSON export)
        result = extract_normative_content(full_text)
        
        return {
            'doc_id': doc_id,
            'status': 'success',
            'pure_text': full_text[:500] + '...' if len(full_text) > 500 else full_text,
            'text_length': len(full_text),
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


def analyze_all_json_exports(input_dir: str, output_file: str = 'normative_analysis_all.json'):
    """
    Analyze all JSON export files and export results.
    
    Args:
        input_dir: Directory containing JSON export files
        output_file: Output JSON file path
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ Directory not found: {input_dir}")
        return
    
    # Get all JSON files
    json_files = sorted(list(input_path.glob("*.json")))
    
    if not json_files:
        print(f"❌ No JSON files found in {input_dir}")
        return
    
    total_docs = len(json_files)
    
    print("="*80)
    print("NORMATIVE CONTENT ANALYSIS - JSON EXPORTS")
    print("="*80)
    print(f"Input directory: {input_dir}")
    print(f"Total JSON files: {total_docs}")
    print(f"Output file: {output_file}")
    print("="*80 + "\n")
    
    results = []
    start_time = time.time()
    
    # Process each JSON file
    for i, json_file in enumerate(json_files, 1):
        print(f"[{i}/{total_docs}] {json_file.name}...", end=' ')
        
        doc_result = process_json_export(json_file)
        results.append(doc_result)
        
        if doc_result['status'] == 'success':
            extracted = doc_result['extracted']
            print(f"OK O:{len(extracted['obligations'])} P:{len(extracted['prohibitions'])} Pe:{len(extracted['permissions'])} D:{len(extracted['definitions'])}")
        else:
            print(f"ERR {doc_result['error']}")
    
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
    print(f"Documents:     {total_docs}")
    print(f"Successful:    {successful}")
    print(f"Failed:        {failed}")
    print(f"Time:          {total_time:.1f}s ({total_time/total_docs:.2f}s/doc)")
    print("\n" + "-"*80)
    print("EXTRACTED:")
    print("-"*80)
    print(f"Obligations:   {total_obligations}")
    print(f"Prohibitions:  {total_prohibitions}")
    print(f"Permissions:   {total_permissions}")
    print(f"Definitions:   {total_definitions}")
    print(f"Total:         {total_extracted}")
    print(f"Avg/doc:       {total_extracted/successful:.1f}" if successful > 0 else "N/A")
    print("="*80)
    print(f"\nSaved: {output_file}")
    print("="*80 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'normative_analysis_all.json'
    else:
        input_dir = 'test_data/json_output'
        output_file = 'normative_analysis_all.json'
    
    analyze_all_json_exports(input_dir, output_file)

# Made with Bob
