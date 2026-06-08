"""
Test script for Enhanced Batch Processor
Tests semantic extraction integration on sample documents
"""

import sys
import json
from pathlib import Path

def test_enhanced_processor():
    """Test enhanced processor on sample documents."""
    
    print("="*80)
    print("TESTING ENHANCED BATCH PROCESSOR")
    print("="*80)
    print()
    
    # Test parameters
    input_dir = "test_data/documents2"
    output_dir = "test_output/enhanced"
    max_docs = 5
    
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Max documents: {max_docs}")
    print()
    
    # Check if input directory exists
    if not Path(input_dir).exists():
        print(f"[ERROR] Input directory not found: {input_dir}")
        print("   Please ensure test documents are in test_data/documents2/")
        return False
    
    # Run enhanced processor
    print("Starting enhanced processor...")
    print("-"*80)
    
    import subprocess
    result = subprocess.run([
        sys.executable,
        "batch_processor_enhanced.py",
        "--input-dir", input_dir,
        "--output-dir", output_dir,
        "--max-documents", str(max_docs),
        "--restart-interval", "10"
    ], capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"\n[ERROR] Enhanced processor failed with exit code: {result.returncode}")
        return False
    
    print("\n" + "="*80)
    print("VERIFYING OUTPUT")
    print("="*80)
    print()
    
    # Check output files
    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"[ERROR] Output directory not created: {output_dir}")
        return False
    
    json_files = list(output_path.glob("*_enhanced.json"))
    
    if not json_files:
        print(f"[ERROR] No output JSON files found in {output_dir}")
        return False
    
    print(f"[OK] Found {len(json_files)} output files")
    print()
    
    # Analyze first output file
    first_file = json_files[0]
    print(f"Analyzing: {first_file.name}")
    print("-"*80)
    
    try:
        with open(first_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check structure
        print("\n[STRUCTURE] Document Structure:")
        print(f"  Document ID: {data.get('document_id', 'N/A')}")
        print(f"  Processed at: {data.get('processed_at', 'N/A')}")
        
        # Check parsed structure
        if 'parsed_structure' in data:
            units = data['parsed_structure'].get('units', [])
            print(f"  Legal units: {len(units)}")
        
        # Check entities
        if 'entities_by_unit' in data:
            total_entities = sum(len(entities) for entities in data['entities_by_unit'].values())
            print(f"  Total entities: {total_entities}")
        
        # Check assertions
        if 'assertions_by_unit' in data:
            total_assertions = sum(len(assertions) for assertions in data['assertions_by_unit'].values())
            print(f"  Total assertions: {total_assertions}")
        
        # Check conditions
        if 'conditions_by_unit' in data:
            total_conditions = sum(len(conditions) for conditions in data['conditions_by_unit'].values())
            print(f"  Total conditions: {total_conditions}")
        
        # Check semantic extraction
        if 'semantic_extraction' in data and data['semantic_extraction']:
            semantic = data['semantic_extraction']
            
            print("\n[SEMANTIC] Semantic Extraction:")
            
            # Normative content
            if 'normative_content' in semantic:
                norm = semantic['normative_content']
                print(f"\n  Normative Content (Total: {norm.get('total_count', 0)}):")
                print(f"    - Obligations: {len(norm.get('obligations', []))}")
                print(f"    - Prohibitions: {len(norm.get('prohibitions', []))}")
                print(f"    - Permissions: {len(norm.get('permissions', []))}")
                print(f"    - Definitions: {len(norm.get('definitions', []))}")
                print(f"    - Waivers: {len(norm.get('waivers', []))}")
                print(f"    - Transfers: {len(norm.get('transfers', []))}")
                print(f"    - Assignments: {len(norm.get('assignments', []))}")
                
                # Show example
                if norm.get('obligations'):
                    print(f"\n    Example obligation:")
                    print(f"      \"{norm['obligations'][0]['text'][:100]}...\"")
            
            # Procedural content
            if 'procedural_content' in semantic:
                proc = semantic['procedural_content']
                print(f"\n  Procedural Content (Total: {proc.get('total_count', 0)}):")
                print(f"    - Steps: {len(proc.get('steps', []))}")
                print(f"    - Sequences: {len(proc.get('sequences', []))}")
                print(f"    - Actors: {len(proc.get('actors', []))}")
            
            # Conditional logic
            if 'conditional_logic' in semantic:
                cond = semantic['conditional_logic']
                print(f"\n  Conditional Logic (Total: {cond.get('total_count', 0)}):")
                print(f"    - IF-THEN patterns: {len(cond.get('if_then_patterns', []))}")
                print(f"    - UNLESS patterns: {len(cond.get('unless_patterns', []))}")
            
            # Temporal references
            if 'temporal_references' in semantic:
                temp = semantic['temporal_references']
                print(f"\n  Temporal References (Total: {temp.get('total_count', 0)}):")
                print(f"    - Absolute dates: {len(temp.get('absolute_dates', []))}")
                print(f"    - Relative dates: {len(temp.get('relative_dates', []))}")
                print(f"    - Deadlines: {len(temp.get('deadlines', []))}")
            
            # Legal hierarchy
            if 'legal_hierarchy' in semantic:
                hier = semantic['legal_hierarchy']
                print(f"\n  Legal Hierarchy:")
                print(f"    - Document type: {hier.get('document_type', 'N/A')}")
                print(f"    - Hierarchy level: {hier.get('hierarchy_level', 'N/A')}")
                print(f"    - Confidence: {hier.get('confidence', 0):.2f}")
            
            # Quantitative data
            if 'quantitative_data' in semantic:
                quant = semantic['quantitative_data']
                print(f"\n  Quantitative Data (Total: {quant.get('total_count', 0)}):")
                print(f"    - Numbers: {len(quant.get('numbers', []))}")
                print(f"    - Thresholds: {len(quant.get('thresholds', []))}")
                print(f"    - Standards: {len(quant.get('standards', []))}")
        else:
            print("\n[WARNING] No semantic extraction data found")
            print("   (Semantic modules may be disabled)")
        
        print("\n" + "="*80)
        print("[SUCCESS] TEST PASSED - Enhanced processor working correctly!")
        print("="*80)
        print()
        print(f"Output files saved to: {output_dir}")
        print(f"Total files processed: {len(json_files)}")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error analyzing output: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_enhanced_processor()
    sys.exit(0 if success else 1)

# Made with Bob
