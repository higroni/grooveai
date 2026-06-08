"""
Convert processed JSON files to Qdrant-compatible format

Converts files from process_single_document.py format to the format
expected by Qdrant loader (same as test_data/json_output format).
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def convert_processed_to_qdrant_format(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert processed JSON to Qdrant-compatible format
    
    Args:
        processed_data: Data from process_single_document.py
        
    Returns:
        Data in Qdrant-compatible format
    """
    # Extract parsed structure
    parsed_structure = processed_data.get('parsed_structure', {})
    units = parsed_structure.get('units', [])
    
    # Convert units to legal_units format
    legal_units = []
    
    for unit in units:
        # Get entities for this unit
        unit_id = unit.get('unit_id', '')
        entities_by_unit = processed_data.get('entities_by_unit', {})
        unit_entities = entities_by_unit.get(unit_id, [])
        
        # Get assertions for this unit
        assertions_by_unit = processed_data.get('assertions_by_unit', {})
        unit_assertions = assertions_by_unit.get(unit_id, [])
        
        # Get conditions for this unit
        conditions_by_unit = processed_data.get('conditions_by_unit', {})
        unit_conditions = conditions_by_unit.get(unit_id, [])
        
        # Build legal unit
        legal_unit = {
            'legal_unit_id': unit_id,
            'document_legal_unit_id': processed_data.get('document_legal_unit_id', ''),
            'parent_legal_unit_id': unit.get('parent_id') or processed_data.get('document_legal_unit_id', ''),
            'unit_type': unit.get('unit_type', 'unknown'),
            'hierarchy_level': unit.get('level', 0),
            'hierarchy_path': unit.get('path', ''),
            'title': unit.get('title', unit.get('heading', '')),
            'content': unit.get('text', ''),
            'content_latinized': unit.get('text', ''),  # Already latinized
            'char_count': len(unit.get('text', '')),
            'word_count': len(unit.get('text', '').split()),
            'entities': unit_entities,
            'assertions': unit_assertions,
            'normative_assertions': [],  # Will be populated from semantic_extraction
            'conditions': unit_conditions
        }
        
        legal_units.append(legal_unit)
    
    # Extract normative assertions from semantic_extraction if available
    semantic_data = processed_data.get('semantic_extraction', {})
    if semantic_data:
        normative_content = semantic_data.get('normative_content', {})
        normative_items = normative_content.get('items', [])
        
        # Try to match normative items to legal units
        # This is approximate since we don't have exact mapping
        for item in normative_items:
            item_text = item.get('text', '')
            # Find best matching unit by content similarity
            for unit in legal_units:
                if item_text in unit['content']:
                    unit['normative_assertions'].append({
                        'type': item.get('type', 'unknown'),
                        'text': item_text,
                        'text_latinized': item_text,
                        'conditions': []
                    })
                    break
    
    # Build document metadata
    doc_metadata = processed_data.get('document_metadata', {})
    
    # Calculate statistics
    total_chars = sum(unit['char_count'] for unit in legal_units)
    total_words = sum(unit['word_count'] for unit in legal_units)
    total_normative = sum(len(unit['normative_assertions']) for unit in legal_units)
    
    document_metadata = {
        'document_id': processed_data.get('document_id', ''),
        'document_legal_unit_id': processed_data.get('document_legal_unit_id', ''),
        'title': doc_metadata.get('title', processed_data.get('document_title', '')),
        'document_type': doc_metadata.get('document_type', 'unknown'),
        'effective_date': None,
        'total_chars': total_chars,
        'total_words': total_words,
        'processed_at': doc_metadata.get('processed_at', processed_data.get('processed_at', '')),
        'processing_time_seconds': None
    }
    
    # Build final output
    output = {
        'document_metadata': document_metadata,
        'legal_units': legal_units
    }
    
    return output


def convert_file(input_path: Path, output_path: Path) -> bool:
    """
    Convert a single file
    
    Args:
        input_path: Path to processed JSON file
        output_path: Path to output Qdrant-compatible JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read input
        with open(input_path, 'r', encoding='utf-8') as f:
            processed_data = json.load(f)
        
        # Convert
        qdrant_data = convert_processed_to_qdrant_format(processed_data)
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(qdrant_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Error converting {input_path.name}: {e}")
        return False


def convert_directory(input_dir: Path, output_dir: Path) -> None:
    """
    Convert all JSON files in a directory
    
    Args:
        input_dir: Directory containing processed JSON files
        output_dir: Directory for Qdrant-compatible JSON files
    """
    # Find all JSON files
    json_files = list(input_dir.glob("*_processed.json"))
    
    if not json_files:
        print(f"No *_processed.json files found in {input_dir}")
        return
    
    total = len(json_files)
    print(f"\nConverting {total} files...")
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")
    print("=" * 80)
    
    converted = 0
    failed = 0
    
    for i, input_file in enumerate(json_files, 1):
        # Generate output filename (remove _processed suffix)
        output_name = input_file.stem.replace('_processed', '_export') + '.json'
        output_file = output_dir / output_name
        
        print(f"[{i}/{total}] {input_file.name} -> {output_name}")
        
        if convert_file(input_file, output_file):
            converted += 1
        else:
            failed += 1
    
    print("=" * 80)
    print(f"\nConversion complete!")
    print(f"  Converted: {converted}/{total}")
    print(f"  Failed: {failed}")
    
    if converted > 0:
        print(f"\nOutput files ready for Qdrant import:")
        print(f"  {output_dir}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python convert_processed_to_qdrant_format.py <input_dir> [output_dir]")
        print("\nExample:")
        print("  python convert_processed_to_qdrant_format.py test_output/batch_230_docs_v3")
        print("  python convert_processed_to_qdrant_format.py test_output/batch_230_docs_v3 test_data/json_output_v3")
        sys.exit(1)
    
    input_dir = Path(sys.argv[1])
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)
    
    # Default output directory
    if len(sys.argv) >= 3:
        output_dir = Path(sys.argv[2])
    else:
        output_dir = Path("test_data/json_output_converted")
    
    convert_directory(input_dir, output_dir)


if __name__ == "__main__":
    main()

# Made with Bob
