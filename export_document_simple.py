#!/usr/bin/env python3
"""
Simple Document Export to JSON

Exports assertions with their entities, conditions, and classifications for a single document.

Usage:
    python export_document_simple.py <document_name> [--output output.json]
    
Example:
    python export_document_simple.py "radni_odnosi_0001_000001.pdf"
"""

import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys


def export_document(db_path: str, document_name: str, import_run_id: Optional[str] = None) -> Dict[str, Any]:
    """Export document with assertions, entities, conditions, and classifications."""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Get document info and full latinized text
        cursor.execute("""
            SELECT job_id, file_path, char_count, page_count, output_text, created_at
            FROM file_reader_jobs
            WHERE file_path LIKE ? AND status = 'success'
            ORDER BY created_at DESC
            LIMIT 1
        """, (f"%{document_name}%",))
        
        doc_row = cursor.fetchone()
        if not doc_row:
            raise ValueError(f"Document not found: {document_name}")
        
        doc_job_id = doc_row["job_id"]
        
        # Get latinized text
        cursor.execute("""
            SELECT output_text
            FROM latinizer_jobs
            ORDER BY created_at DESC
            LIMIT 1
        """)
        latinizer_row = cursor.fetchone()
        latinized_text = latinizer_row["output_text"] if latinizer_row else doc_row["output_text"]
        
        # 2. Get all assertions for this document
        cursor.execute("""
            SELECT 
                job_id as assertion_job_id,
                legal_unit_id,
                output_assertions
            FROM extraction_jobs
            WHERE job_id LIKE ?
        """, (f"{doc_job_id}%",))
        
        assertions_data = []
        assertion_ids = []
        
        for row in cursor.fetchall():
            try:
                assertions_list = json.loads(row["output_assertions"])
                for assertion in assertions_list:
                    assertion_id = assertion.get("assertion_id")
                    if assertion_id:
                        assertions_data.append({
                            "assertion_id": assertion_id,
                            "text": assertion.get("text", ""),
                            "confidence": assertion.get("confidence", 0.0)
                        })
                        assertion_ids.append(assertion_id)
            except json.JSONDecodeError:
                continue
        
        if not assertions_data:
            print(f"[WARNING] No assertions found for document: {document_name}")
            return {
                "import_run_id": import_run_id or doc_job_id,
                "document": {
                    "name": Path(doc_row["file_path"]).name,
                    "path": doc_row["file_path"],
                    "char_count": doc_row["char_count"],
                    "page_count": doc_row["page_count"],
                    "processed_at": doc_row["created_at"]
                },
                "full_text": latinized_text,
                "assertions": [],
                "export_timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        # 3. Get entities for all assertions
        entities_map = {}
        if assertion_ids:
            placeholders = ",".join("?" * len(assertion_ids))
            cursor.execute(f"""
                SELECT 
                    job_id,
                    entity_type,
                    text
                FROM entities
                WHERE job_id IN ({placeholders})
            """, assertion_ids)
            
            for row in cursor.fetchall():
                job_id = row["job_id"]
                if job_id not in entities_map:
                    entities_map[job_id] = []
                entities_map[job_id].append({
                    "text": row["text"],
                    "type": row["entity_type"]
                })
        
        # 4. Get conditions for all assertions
        conditions_map = {}
        if assertion_ids:
            cursor.execute(f"""
                SELECT 
                    job_id,
                    condition_type,
                    text
                FROM extracted_conditions
                WHERE job_id IN ({placeholders})
            """, assertion_ids)
            
            for row in cursor.fetchall():
                job_id = row["job_id"]
                if job_id not in conditions_map:
                    conditions_map[job_id] = []
                conditions_map[job_id].append({
                    "text": row["text"],
                    "type": row["condition_type"]
                })
        
        # 5. Get classifications for all assertions
        classifications_map = {}
        if assertion_ids:
            cursor.execute(f"""
                SELECT 
                    assertion_id,
                    assertion_type,
                    confidence
                FROM classification_jobs
                WHERE assertion_id IN ({placeholders})
            """, assertion_ids)
            
            for row in cursor.fetchall():
                assertion_id = row["assertion_id"]
                classifications_map[assertion_id] = {
                    "type": row["assertion_type"],
                    "confidence": row["confidence"]
                }
        
        # 6. Combine all data
        enriched_assertions = []
        for assertion in assertions_data:
            assertion_id = assertion["assertion_id"]
            
            enriched_assertions.append({
                "assertion_id": assertion_id,
                "text": assertion["text"],
                "confidence": assertion["confidence"],
                "entities": entities_map.get(assertion_id, []),
                "conditions": conditions_map.get(assertion_id, []),
                "classification": classifications_map.get(assertion_id, {})
            })
        
        # 7. Build final structure
        result = {
            "import_run_id": import_run_id or doc_job_id,
            "document": {
                "name": Path(doc_row["file_path"]).name,
                "path": doc_row["file_path"],
                "char_count": doc_row["char_count"],
                "page_count": doc_row["page_count"],
                "processed_at": doc_row["created_at"]
            },
            "full_text": latinized_text,
            "assertions": enriched_assertions,
            "export_timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return result
        
    finally:
        conn.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export document assertions with entities, conditions, and classifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python export_document_simple.py "radni_odnosi_0001_000001.pdf"
  python export_document_simple.py "radni_odnosi_0001_000001.pdf" --output doc1.json
  python export_document_simple.py "document.pdf" --db custom.db
        """
    )
    
    parser.add_argument(
        "document_name",
        help="Document name (e.g., 'radni_odnosi_0001_000001.pdf')"
    )
    
    parser.add_argument(
        "--import-run-id",
        help="Import run ID for tracking (default: document job_id)",
        default=None
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file path (default: <document_name>_export.json)",
        default=None
    )
    
    parser.add_argument(
        "--db",
        help="Database file path (default: data/databases/grooveai_unified.db)",
        default="data/databases/grooveai_unified.db"
    )
    
    parser.add_argument(
        "--compact",
        help="Output compact JSON (no pretty printing)",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        doc_name = Path(args.document_name).stem
        output_path = f"{doc_name}_export.json"
    
    # Export document
    try:
        print(f"Exporting document: {args.document_name}")
        print(f"Database: {args.db}")
        if args.import_run_id:
            print(f"Import Run ID: {args.import_run_id}")
        
        result = export_document(args.db, args.document_name, args.import_run_id)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            if args.compact:
                json.dump(result, f, ensure_ascii=False)
            else:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Successfully exported to: {output_path}")
        print(f"\nImport Run ID: {result['import_run_id']}")
        print(f"Assertions: {len(result['assertions'])}")
        print(f"Full text length: {len(result['full_text'])} characters")
        print(f"File size: {Path(output_path).stat().st_size:,} bytes")
        
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
