#!/usr/bin/env python3
"""
Export Document to JSON for Vector Database Import

This script exports all pipeline results for a single document from the unified database
into a structured JSON file suitable for vector database import.

Usage:
    python export_document_to_json.py <document_name> [--output output.json] [--db database.db]
    
Example:
    python export_document_to_json.py "radni_odnosi_0001_000001.pdf"
    python export_document_to_json.py "radni_odnosi_0001_000001.pdf" --output doc1.json
"""

import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys


class DocumentExporter:
    """Export complete document data from unified database to JSON."""
    
    def __init__(self, db_path: str = "data/databases/grooveai_unified.db"):
        """Initialize exporter with database path."""
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self):
        """Connect to database."""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def get_document_metadata(self, document_name: str) -> Optional[Dict]:
        """Get document metadata from file_reader_jobs table."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                job_id,
                file_path,
                char_count,
                page_count,
                processing_time_ms,
                created_at
            FROM file_reader_jobs
            WHERE file_path LIKE ? AND status = 'success'
            ORDER BY created_at DESC
            LIMIT 1
        """, (f"%{document_name}%",))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "job_id": row["job_id"],
            "file_path": row["file_path"],
            "file_name": Path(row["file_path"]).name,
            "char_count": row["char_count"],
            "page_count": row["page_count"],
            "processing_time_ms": row["processing_time_ms"],
            "processed_at": row["created_at"]
        }
    
    def get_legal_units(self, job_id: str) -> List[Dict]:
        """Get parsed legal units from parser_jobs table."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                legal_unit_id,
                unit_type,
                unit_number,
                title,
                content,
                hierarchy_level,
                parent_id
            FROM parser_jobs
            WHERE job_id = ?
            ORDER BY hierarchy_level, unit_number
        """, (job_id,))
        
        units = []
        for row in cursor.fetchall():
            units.append({
                "legal_unit_id": row["legal_unit_id"],
                "type": row["unit_type"],
                "number": row["unit_number"],
                "title": row["title"],
                "content": row["content"],
                "hierarchy_level": row["hierarchy_level"],
                "parent_id": row["parent_id"]
            })
        
        return units
    
    def get_assertions(self, job_id: str) -> List[Dict]:
        """Get extracted assertions from extraction_jobs table."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                job_id as assertion_job_id,
                legal_unit_id,
                output_assertions,
                total_assertions,
                processing_time_ms,
                created_at
            FROM extraction_jobs
            WHERE job_id LIKE ?
            ORDER BY created_at
        """, (f"{job_id}%",))
        
        assertions = []
        for row in cursor.fetchall():
            # Parse JSON assertions
            try:
                assertion_list = json.loads(row["output_assertions"])
                for assertion in assertion_list:
                    assertions.append({
                        "assertion_id": assertion.get("assertion_id"),
                        "legal_unit_id": row["legal_unit_id"],
                        "text": assertion.get("text"),
                        "confidence": assertion.get("confidence"),
                        "sentence_index": assertion.get("sentence_index"),
                        "start_char": assertion.get("start_char"),
                        "end_char": assertion.get("end_char"),
                        "extracted_at": row["created_at"]
                    })
            except json.JSONDecodeError:
                continue
        
        return assertions
    
    def get_entities(self, assertion_ids: List[str]) -> Dict[str, List[Dict]]:
        """Get recognized entities from entity_results table."""
        if not assertion_ids:
            return {}
        
        cursor = self.conn.cursor()
        placeholders = ",".join("?" * len(assertion_ids))
        cursor.execute(f"""
            SELECT 
                assertion_id,
                entity_text,
                entity_type,
                start_pos,
                end_pos,
                confidence,
                created_at
            FROM entity_results
            WHERE assertion_id IN ({placeholders})
            ORDER BY assertion_id, start_pos
        """, assertion_ids)
        
        entities_by_assertion = {}
        for row in cursor.fetchall():
            assertion_id = row["assertion_id"]
            if assertion_id not in entities_by_assertion:
                entities_by_assertion[assertion_id] = []
            
            entities_by_assertion[assertion_id].append({
                "text": row["entity_text"],
                "type": row["entity_type"],
                "start_pos": row["start_pos"],
                "end_pos": row["end_pos"],
                "confidence": row["confidence"],
                "recognized_at": row["created_at"]
            })
        
        return entities_by_assertion
    
    def get_conditions(self, assertion_ids: List[str]) -> Dict[str, List[Dict]]:
        """Get extracted conditions from condition_results table."""
        if not assertion_ids:
            return {}
        
        cursor = self.conn.cursor()
        placeholders = ",".join("?" * len(assertion_ids))
        cursor.execute(f"""
            SELECT 
                assertion_id,
                condition_text,
                condition_type,
                trigger_words,
                confidence,
                created_at
            FROM condition_results
            WHERE assertion_id IN ({placeholders})
            ORDER BY assertion_id
        """, assertion_ids)
        
        conditions_by_assertion = {}
        for row in cursor.fetchall():
            assertion_id = row["assertion_id"]
            if assertion_id not in conditions_by_assertion:
                conditions_by_assertion[assertion_id] = []
            
            conditions_by_assertion[assertion_id].append({
                "text": row["condition_text"],
                "type": row["condition_type"],
                "trigger_words": row["trigger_words"],
                "confidence": row["confidence"],
                "extracted_at": row["created_at"]
            })
        
        return conditions_by_assertion
    
    def get_classifications(self, assertion_ids: List[str]) -> Dict[str, Dict]:
        """Get classifications from classifier_results table."""
        if not assertion_ids:
            return {}
        
        cursor = self.conn.cursor()
        placeholders = ",".join("?" * len(assertion_ids))
        cursor.execute(f"""
            SELECT 
                assertion_id,
                primary_category,
                confidence,
                all_categories,
                created_at
            FROM classifier_results
            WHERE assertion_id IN ({placeholders})
        """, assertion_ids)
        
        classifications = {}
        for row in cursor.fetchall():
            try:
                all_cats = json.loads(row["all_categories"]) if row["all_categories"] else []
            except json.JSONDecodeError:
                all_cats = []
            
            classifications[row["assertion_id"]] = {
                "primary_category": row["primary_category"],
                "confidence": row["confidence"],
                "all_categories": all_cats,
                "classified_at": row["created_at"]
            }
        
        return classifications
    
    def get_enrichments(self, assertion_ids: List[str]) -> Dict[str, Dict]:
        """Get enrichments from enrichment_results table."""
        if not assertion_ids:
            return {}
        
        cursor = self.conn.cursor()
        placeholders = ",".join("?" * len(assertion_ids))
        cursor.execute(f"""
            SELECT 
                assertion_id,
                enriched_data,
                knowledge_sources,
                confidence,
                created_at
            FROM enrichment_results
            WHERE assertion_id IN ({placeholders})
        """, assertion_ids)
        
        enrichments = {}
        for row in cursor.fetchall():
            try:
                enriched = json.loads(row["enriched_data"]) if row["enriched_data"] else {}
                sources = json.loads(row["knowledge_sources"]) if row["knowledge_sources"] else []
            except json.JSONDecodeError:
                enriched = {}
                sources = []
            
            enrichments[row["assertion_id"]] = {
                "enriched_data": enriched,
                "knowledge_sources": sources,
                "confidence": row["confidence"],
                "enriched_at": row["created_at"]
            }
        
        return enrichments
    
    def export_document(self, document_name: str) -> Dict[str, Any]:
        """Export complete document data to structured dictionary."""
        # Get document metadata
        metadata = self.get_document_metadata(document_name)
        if not metadata:
            raise ValueError(f"Document not found: {document_name}")
        
        job_id = metadata["job_id"]
        
        # Get legal units
        legal_units = self.get_legal_units(job_id)
        
        # Get assertions
        assertions = self.get_assertions(job_id)
        assertion_ids = [a["assertion_id"] for a in assertions if a["assertion_id"]]
        
        # Get related data
        entities_map = self.get_entities(assertion_ids)
        conditions_map = self.get_conditions(assertion_ids)
        classifications_map = self.get_classifications(assertion_ids)
        enrichments_map = self.get_enrichments(assertion_ids)
        
        # Build complete structure
        enriched_assertions = []
        for assertion in assertions:
            assertion_id = assertion["assertion_id"]
            
            enriched_assertion = {
                **assertion,
                "entities": entities_map.get(assertion_id, []),
                "conditions": conditions_map.get(assertion_id, []),
                "classification": classifications_map.get(assertion_id, {}),
                "enrichment": enrichments_map.get(assertion_id, {})
            }
            enriched_assertions.append(enriched_assertion)
        
        # Build final document structure
        document = {
            "metadata": {
                **metadata,
                "export_timestamp": datetime.utcnow().isoformat() + "Z",
                "exporter_version": "1.0.0"
            },
            "legal_structure": {
                "units": legal_units,
                "total_units": len(legal_units)
            },
            "assertions": {
                "items": enriched_assertions,
                "total_assertions": len(enriched_assertions),
                "total_entities": sum(len(a["entities"]) for a in enriched_assertions),
                "total_conditions": sum(len(a["conditions"]) for a in enriched_assertions),
                "classified_count": sum(1 for a in enriched_assertions if a["classification"]),
                "enriched_count": sum(1 for a in enriched_assertions if a["enrichment"])
            },
            "statistics": {
                "legal_units": len(legal_units),
                "assertions": len(enriched_assertions),
                "entities": sum(len(a["entities"]) for a in enriched_assertions),
                "conditions": sum(len(a["conditions"]) for a in enriched_assertions),
                "classifications": sum(1 for a in enriched_assertions if a["classification"]),
                "enrichments": sum(1 for a in enriched_assertions if a["enrichment"])
            }
        }
        
        return document
    
    def export_to_file(self, document_name: str, output_path: str, pretty: bool = True):
        """Export document to JSON file."""
        try:
            self.connect()
            document = self.export_document(document_name)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(document, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(document, f, ensure_ascii=False)
            
            print(f"✅ Successfully exported document to: {output_path}")
            print(f"\nDocument Statistics:")
            print(f"  - Legal Units: {document['statistics']['legal_units']}")
            print(f"  - Assertions: {document['statistics']['assertions']}")
            print(f"  - Entities: {document['statistics']['entities']}")
            print(f"  - Conditions: {document['statistics']['conditions']}")
            print(f"  - Classifications: {document['statistics']['classifications']}")
            print(f"  - Enrichments: {document['statistics']['enrichments']}")
            print(f"\nFile size: {Path(output_path).stat().st_size:,} bytes")
            
        finally:
            self.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export document from unified database to JSON for vector database import",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export with default output name
  python export_document_to_json.py "radni_odnosi_0001_000001.pdf"
  
  # Export with custom output name
  python export_document_to_json.py "radni_odnosi_0001_000001.pdf" --output doc1.json
  
  # Export from different database
  python export_document_to_json.py "document.pdf" --db custom.db
  
  # Export compact JSON (no pretty printing)
  python export_document_to_json.py "document.pdf" --compact
        """
    )
    
    parser.add_argument(
        "document_name",
        help="Document name or path (e.g., 'radni_odnosi_0001_000001.pdf')"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file path (default: <document_name>.json)",
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
        # Use document name as base
        doc_name = Path(args.document_name).stem
        output_path = f"{doc_name}_export.json"
    
    # Export document
    try:
        exporter = DocumentExporter(db_path=args.db)
        exporter.export_to_file(
            document_name=args.document_name,
            output_path=output_path,
            pretty=not args.compact
        )
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
