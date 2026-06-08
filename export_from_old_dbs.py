"""
Export document data from OLD separate database structure.
This reads from the performance test data stored in separate module databases.
"""
import sqlite3
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


def export_document_from_old_dbs(
    document_name: str,
    import_run_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Export document data from old separate databases.
    
    Args:
        document_name: Name of the document (e.g., "radni_odnosi_0001_000001.pdf")
        import_run_id: Optional import run identifier for tracking
        
    Returns:
        Dictionary containing all document data
    """
    
    # Database paths
    db_dir = Path("data/databases")
    file_reader_db = db_dir / "file_reader.db"
    latinizer_db = db_dir / "latinizer.db"
    parser_db = db_dir / "legal_parser.db"
    assertion_db = db_dir / "assertion_extractor.db"
    entity_db = db_dir / "entity_recognizer.db"
    condition_db = db_dir / "condition_extractor.db"
    classifier_db = db_dir / "assertion_classifier.db"
    
    result = {
        "import_run_id": import_run_id or f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "document": {},
        "full_text": "",
        "assertions": [],
        "export_timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    print(f"Exporting document: {document_name}")
    print(f"Import Run ID: {result['import_run_id']}")
    
    # 1. Get document metadata from file_reader
    if file_reader_db.exists():
        conn = sqlite3.connect(file_reader_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT job_id, file_path, file_type, char_count, page_count, created_at
            FROM file_reader_jobs
            WHERE file_path LIKE ?
            LIMIT 1
        """, (f"%{document_name}%",))
        row = cursor.fetchone()
        if row:
            result["document"] = {
                "job_id": row[0],
                "name": document_name,
                "file_path": row[1],
                "file_type": row[2],
                "char_count": row[3],
                "page_count": row[4],
                "processed_at": row[5]
            }
            print(f"[OK] Found document: {row[3]} chars, {row[4]} pages")
        conn.close()
    
    # 2. Get latinized text from latinizer
    if latinizer_db.exists():
        conn = sqlite3.connect(latinizer_db)
        cursor = conn.cursor()
        
        # Check schema first
        cursor.execute("PRAGMA table_info(latinizer_jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Try to find the document
        if "filename" in columns:
            cursor.execute("""
                SELECT output_text
                FROM latinizer_jobs
                WHERE filename LIKE ?
                LIMIT 1
            """, (f"%{document_name}%",))
        else:
            cursor.execute("""
                SELECT output_text
                FROM latinizer_jobs
                LIMIT 1
            """)
        
        row = cursor.fetchone()
        if row:
            result["full_text"] = row[0] or ""
            print(f"[OK] Found latinized text: {len(result['full_text'])} chars")
        conn.close()
    
    # 3. Get legal units from parser
    legal_units = {}
    if parser_db.exists():
        conn = sqlite3.connect(parser_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, canonical_json
            FROM legal_parser_jobs
            WHERE filename LIKE ?
        """, (f"%{document_name}%",))
        
        for row in cursor.fetchall():
            parser_job_id = row[0]
            canonical_json = row[1]
            if canonical_json:
                try:
                    units = json.loads(canonical_json)
                    if isinstance(units, list):
                        for unit in units:
                            if isinstance(unit, dict):
                                unit_id = unit.get("id")
                                if unit_id:
                                    legal_units[unit_id] = unit
                except (json.JSONDecodeError, AttributeError, TypeError) as e:
                    print(f"[WARNING] Failed to parse legal units: {e}")
        
        print(f"[OK] Found {len(legal_units)} legal units")
        conn.close()
    
    # 4. Get assertions from assertion_extractor
    assertions_by_unit = {}
    if assertion_db.exists():
        conn = sqlite3.connect(assertion_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT legal_unit_id, output_assertions, total_assertions
            FROM extraction_jobs
        """)
        
        for row in cursor.fetchall():
            unit_id = row[0]
            output_json = row[1]
            total = row[2]
            
            if output_json:
                try:
                    assertions = json.loads(output_json)
                    if isinstance(assertions, list):
                        assertions_by_unit[unit_id] = assertions
                except json.JSONDecodeError:
                    pass
        
        total_assertions = sum(len(a) for a in assertions_by_unit.values())
        print(f"[OK] Found {total_assertions} assertions across {len(assertions_by_unit)} units")
        conn.close()
    
    # 5. Get entities from entity_recognizer
    entities_by_unit = {}
    if entity_db.exists():
        conn = sqlite3.connect(entity_db)
        cursor = conn.cursor()
        
        # Check schema
        cursor.execute("PRAGMA table_info(recognition_jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"[DEBUG] entity_recognizer columns: {columns}")
        
        # Find the right columns
        id_col = "legal_unit_id" if "legal_unit_id" in columns else "job_id"
        data_col = None
        for col in ["entities_json", "output_entities", "entities", "result_json"]:
            if col in columns:
                data_col = col
                break
        
        if data_col:
            cursor.execute(f"""
                SELECT {id_col}, {data_col}
                FROM recognition_jobs
            """)
        else:
            print(f"[WARNING] No entities data column found in entity_recognizer")
            conn.close()
            entities_by_unit = {}
        
        for row in cursor.fetchall():
            unit_id = row[0]
            entities_json = row[1]
            
            if entities_json:
                try:
                    entities = json.loads(entities_json)
                    if isinstance(entities, list):
                        entities_by_unit[unit_id] = entities
                except json.JSONDecodeError:
                    pass
        
        print(f"[OK] Found entities for {len(entities_by_unit)} units")
        conn.close()
    
    # 6. Get conditions from condition_extractor
    conditions_by_unit = {}
    if condition_db.exists():
        conn = sqlite3.connect(condition_db)
        cursor = conn.cursor()
        
        # Check schema
        cursor.execute("PRAGMA table_info(condition_extraction_jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"[DEBUG] condition_extractor columns: {columns}")
        
        # Find the right columns
        id_col = "legal_unit_id" if "legal_unit_id" in columns else "job_id"
        data_col = None
        for col in ["conditions_json", "output_conditions", "conditions", "result_json"]:
            if col in columns:
                data_col = col
                break
        
        if data_col:
            cursor.execute(f"""
                SELECT {id_col}, {data_col}
                FROM condition_extraction_jobs
            """)
        else:
            print(f"[WARNING] No conditions data column found in condition_extractor")
            conn.close()
            conditions_by_unit = {}
        
        for row in cursor.fetchall():
            unit_id = row[0]
            conditions_json = row[1]
            
            if conditions_json:
                try:
                    conditions = json.loads(conditions_json)
                    if isinstance(conditions, list):
                        conditions_by_unit[unit_id] = conditions
                except json.JSONDecodeError:
                    pass
        
        print(f"[OK] Found conditions for {len(conditions_by_unit)} units")
        conn.close()
    
    # 7. Get classifications from assertion_classifier
    classifications_by_assertion = {}
    if classifier_db.exists():
        conn = sqlite3.connect(classifier_db)
        cursor = conn.cursor()
        
        # Check schema
        cursor.execute("PRAGMA table_info(classification_jobs)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"[DEBUG] assertion_classifier columns: {columns}")
        
        # Find the right columns
        id_col = "assertion_id" if "assertion_id" in columns else "job_id"
        type_col = None
        conf_col = None
        
        for col in ["classification_type", "predicted_class", "class_type", "type"]:
            if col in columns:
                type_col = col
                break
        
        for col in ["confidence", "score", "probability"]:
            if col in columns:
                conf_col = col
                break
        
        if type_col and conf_col:
            cursor.execute(f"""
                SELECT {id_col}, {type_col}, {conf_col}
                FROM classification_jobs
            """)
            
            for row in cursor.fetchall():
                assertion_id = row[0]
                class_type = row[1]
                confidence = row[2]
                
                classifications_by_assertion[assertion_id] = {
                    "type": class_type,
                    "confidence": confidence
                }
        else:
            print(f"[WARNING] No classification columns found in assertion_classifier")
        
        print(f"[OK] Found classifications for {len(classifications_by_assertion)} assertions")
        conn.close()
    
    # 8. Combine all data into assertions
    for unit_id, assertions in assertions_by_unit.items():
        unit_entities = entities_by_unit.get(unit_id, [])
        unit_conditions = conditions_by_unit.get(unit_id, [])
        
        for assertion in assertions:
            assertion_id = assertion.get("id")
            assertion_text = assertion.get("text", "")
            
            # Get classification
            classification = classifications_by_assertion.get(assertion_id, {})
            
            result["assertions"].append({
                "assertion_id": assertion_id,
                "legal_unit_id": unit_id,
                "text": assertion_text,
                "entities": unit_entities,
                "conditions": unit_conditions,
                "classification": classification
            })
    
    print(f"\n[OK] Export complete!")
    print(f"  - Assertions: {len(result['assertions'])}")
    print(f"  - Full text: {len(result['full_text'])} characters")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Export document from old separate databases")
    parser.add_argument("document_name", help="Document name (e.g., radni_odnosi_0001_000001.pdf)")
    parser.add_argument("--import-run-id", help="Import run identifier for tracking")
    parser.add_argument("--output", help="Output JSON file path (default: <document_name>_export.json)")
    
    args = parser.parse_args()
    
    # Export data
    data = export_document_from_old_dbs(args.document_name, args.import_run_id)
    
    # Save to file
    output_file = args.output or f"{Path(args.document_name).stem}_export.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] Saved to: {output_file}")
    print(f"  - File size: {Path(output_file).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

# Made with Bob
