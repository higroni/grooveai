"""
Check batch processor results in unified database.
Shows what data was stored from the batch processing run.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def check_unified_db():
    """Check unified database for batch processor results."""
    
    db_path = Path("data/databases/grooveai_unified.db")
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return
    
    print("="*80)
    print("UNIFIED DATABASE ANALYSIS")
    print("="*80)
    print(f"Database: {db_path}")
    print(f"Size: {db_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Tables in database: {len(tables)}")
    print()
    
    # Check each table
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} rows")
    
    print()
    print("="*80)
    print("RECENT BATCH PROCESSING DATA")
    print("="*80)
    
    # Check file_reader_jobs (M1)
    print("\n1. FILE READER JOBS (M1)")
    print("-" * 40)
    cursor.execute("""
        SELECT job_id, filename, status, created_at
        FROM file_reader_jobs
        ORDER BY created_at DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  Job: {row[0][:8]}... | File: {row[1]} | Status: {row[2]} | Time: {row[3]}")
    
    # Check extraction_jobs (M7 - Assertions)
    print("\n2. ASSERTION EXTRACTION JOBS (M7)")
    print("-" * 40)
    cursor.execute("""
        SELECT job_id, legal_unit_id, status, assertions_count, created_at
        FROM extraction_jobs
        ORDER BY created_at DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  Job: {row[0][:8]}... | Unit: {row[1][:8] if row[1] else 'N/A'}... | Assertions: {row[3]} | Time: {row[4]}")
    
    # Check recognition_jobs (M6 - Entities)
    print("\n3. ENTITY RECOGNITION JOBS (M6)")
    print("-" * 40)
    cursor.execute("""
        SELECT job_id, legal_unit_id, status, entities_count, created_at
        FROM recognition_jobs
        ORDER BY created_at DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  Job: {row[0][:8]}... | Unit: {row[1][:8] if row[1] else 'N/A'}... | Entities: {row[3]} | Time: {row[4]}")
    
    # Check condition_extraction_jobs (M8)
    print("\n4. CONDITION EXTRACTION JOBS (M8)")
    print("-" * 40)
    cursor.execute("""
        SELECT job_id, assertion_id, status, conditions_count, created_at
        FROM condition_extraction_jobs
        ORDER BY created_at DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  Job: {row[0][:8]}... | Assertion: {row[1][:8] if row[1] else 'N/A'}... | Conditions: {row[3]} | Time: {row[4]}")
    
    # Check classification_jobs (M9)
    print("\n5. CLASSIFICATION JOBS (M9)")
    print("-" * 40)
    cursor.execute("""
        SELECT job_id, assertion_id, status, classification_type, created_at
        FROM classification_jobs
        ORDER BY created_at DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  Job: {row[0][:8]}... | Assertion: {row[1][:8] if row[1] else 'N/A'}... | Type: {row[3]} | Time: {row[4]}")
    
    # Summary statistics
    print()
    print("="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    # Total documents processed
    cursor.execute("SELECT COUNT(DISTINCT filename) FROM file_reader_jobs WHERE status = 'completed'")
    total_docs = cursor.fetchone()[0]
    print(f"Total documents processed: {total_docs}")
    
    # Total legal units
    cursor.execute("SELECT COUNT(*) FROM legal_units")
    total_units = cursor.fetchone()[0]
    print(f"Total legal units: {total_units}")
    
    # Total assertions
    cursor.execute("SELECT COUNT(*) FROM assertions")
    total_assertions = cursor.fetchone()[0]
    print(f"Total assertions: {total_assertions}")
    
    # Total entities
    cursor.execute("SELECT COUNT(*) FROM entities")
    total_entities = cursor.fetchone()[0]
    print(f"Total entities: {total_entities}")
    
    # Total conditions
    cursor.execute("SELECT COUNT(*) FROM conditions")
    total_conditions = cursor.fetchone()[0]
    print(f"Total conditions: {total_conditions}")
    
    # Get most recent document details
    print()
    print("="*80)
    print("MOST RECENT DOCUMENT DETAILS")
    print("="*80)
    
    cursor.execute("""
        SELECT job_id, filename, status, char_count, page_count, created_at
        FROM file_reader_jobs
        ORDER BY created_at DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    if row:
        job_id, filename, status, char_count, page_count, created_at = row
        print(f"\nDocument: {filename}")
        print(f"Job ID: {job_id}")
        print(f"Status: {status}")
        print(f"Characters: {char_count}")
        print(f"Pages: {page_count}")
        print(f"Processed: {created_at}")
        
        # Get legal units for this document
        cursor.execute("""
            SELECT COUNT(*) FROM legal_units WHERE source_uri LIKE ?
        """, (f"%{filename}%",))
        units_count = cursor.fetchone()[0]
        print(f"Legal units: {units_count}")
        
        # Get assertions for this document
        cursor.execute("""
            SELECT COUNT(*) FROM assertions a
            JOIN legal_units lu ON a.legal_unit_id = lu.legal_unit_id
            WHERE lu.source_uri LIKE ?
        """, (f"%{filename}%",))
        assertions_count = cursor.fetchone()[0]
        print(f"Assertions: {assertions_count}")
        
        # Get entities for this document
        cursor.execute("""
            SELECT COUNT(*) FROM entities e
            JOIN legal_units lu ON e.legal_unit_id = lu.legal_unit_id
            WHERE lu.source_uri LIKE ?
        """, (f"%{filename}%",))
        entities_count = cursor.fetchone()[0]
        print(f"Entities: {entities_count}")
        
        # Get conditions for this document
        cursor.execute("""
            SELECT COUNT(*) FROM conditions c
            JOIN assertions a ON c.assertion_id = a.assertion_id
            JOIN legal_units lu ON a.legal_unit_id = lu.legal_unit_id
            WHERE lu.source_uri LIKE ?
        """, (f"%{filename}%",))
        conditions_count = cursor.fetchone()[0]
        print(f"Conditions: {conditions_count}")
    
    conn.close()
    
    print()
    print("="*80)
    print("Analysis complete!")
    print("="*80)

if __name__ == "__main__":
    check_unified_db()

# Made with Bob
