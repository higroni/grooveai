"""
Direct database test for Module 7: Entity Recognizer

Tests that entities are correctly stored in SQLite database.
"""

import sqlite3
import requests
import json
from pathlib import Path

# Module URL
ENTITY_RECOGNIZER_URL = "http://localhost:8107"

# Database path (from config.yaml)
DB_PATH = Path("data/databases/entity_recognizer.db")


def test_database_storage():
    """Test that entities are correctly stored in database."""
    
    print("\n" + "="*80)
    print("MODULE 7: ENTITY RECOGNIZER - DATABASE STORAGE TEST")
    print("="*80)
    
    # Set UTF-8 encoding for Windows console
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Check if database exists
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at: {DB_PATH}")
        return
    
    print(f"[OK] Database found at: {DB_PATH}")
    
    # Test 1: Send recognition request
    print("\n[TEST 1] Send Recognition Request")
    print("-" * 80)
    
    sample_assertion = {
        "assertion_id": "db-test-001",
        "text": "Ministarstvo finansija donosi odluku u Beogradu dana 15. januar 2024. godine.",
        "confidence": 0.90
    }
    
    print(f"Assertion: {sample_assertion['text']}")
    
    try:
        response = requests.post(
            f"{ENTITY_RECOGNIZER_URL}/api/recognize",
            json={
                "assertion": sample_assertion,
                "language": "sr",
                "min_confidence": 0.5
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Recognition failed: {response.status_code}")
            return
        
        result = response.json()
        job_id = result['job_id']
        assertion_id = sample_assertion['assertion_id']
        
        print(f"[OK] Recognition successful")
        print(f"Job ID: {job_id}")
        print(f"Entities found: {result['stats']['total_entities']}")
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return
    
    # Test 2: Check database tables
    print("\n[TEST 2] Check Database Tables")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"[OK] Database tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if required tables exist
        required_tables = ['recognition_jobs', 'entities']
        existing_tables = [t[0] for t in tables]
        
        for table in required_tables:
            if table in existing_tables:
                print(f"[OK] Table '{table}' exists")
            else:
                print(f"[ERROR] Table '{table}' missing!")
        
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        return
    
    # Test 3: Check recognition_jobs table
    print("\n[TEST 3] Check recognition_jobs Table")
    print("-" * 80)
    
    try:
        cursor.execute("""
            SELECT job_id, assertion_id, language, total_entities, avg_confidence, created_at
            FROM recognition_jobs
            WHERE job_id = ?
        """, (job_id,))
        
        job_row = cursor.fetchone()
        
        if job_row:
            print(f"[OK] Job found in database")
            print(f"  Job ID: {job_row[0]}")
            print(f"  Assertion ID: {job_row[1]}")
            print(f"  Language: {job_row[2]}")
            print(f"  Total Entities: {job_row[3]}")
            print(f"  Avg Confidence: {job_row[4]:.2f}")
            print(f"  Created At: {job_row[5]}")
        else:
            print(f"[ERROR] Job not found in database!")
            return
        
    except sqlite3.Error as e:
        print(f"[ERROR] Query failed: {e}")
        return
    
    # Test 4: Check entities table
    print("\n[TEST 4] Check entities Table")
    print("-" * 80)
    
    try:
        cursor.execute("""
            SELECT entity_id, entity_type, text, start_char, end_char, confidence
            FROM entities
            WHERE job_id = ?
            ORDER BY start_char
        """, (job_id,))
        
        entity_rows = cursor.fetchall()
        
        if entity_rows:
            print(f"[OK] Found {len(entity_rows)} entities in database")
            for i, row in enumerate(entity_rows, 1):
                print(f"\n  Entity {i}:")
                print(f"    ID: {row[0]}")
                print(f"    Type: {row[1]}")
                print(f"    Text: '{row[2]}'")
                print(f"    Position: {row[3]}-{row[4]}")
                print(f"    Confidence: {row[5]:.2f}")
        else:
            print(f"[ERROR] No entities found in database!")
            return
        
    except sqlite3.Error as e:
        print(f"[ERROR] Query failed: {e}")
        return
    
    # Test 5: Check entities by assertion_id
    print("\n[TEST 5] Query Entities by Assertion ID")
    print("-" * 80)
    
    try:
        cursor.execute("""
            SELECT e.entity_id, e.entity_type, e.text, e.confidence
            FROM entities e
            JOIN recognition_jobs j ON e.job_id = j.job_id
            WHERE j.assertion_id = ?
            ORDER BY e.start_char
        """, (assertion_id,))
        
        entity_rows = cursor.fetchall()
        
        if entity_rows:
            print(f"[OK] Found {len(entity_rows)} entities for assertion '{assertion_id}'")
            for i, row in enumerate(entity_rows, 1):
                print(f"  {i}. {row[1]}: '{row[2]}' (confidence: {row[3]:.2f})")
        else:
            print(f"[ERROR] No entities found for assertion!")
            return
        
    except sqlite3.Error as e:
        print(f"[ERROR] Query failed: {e}")
        return
    
    # Test 6: Check data integrity
    print("\n[TEST 6] Check Data Integrity")
    print("-" * 80)
    
    try:
        # Check if all entities have valid job_id
        cursor.execute("""
            SELECT COUNT(*) FROM entities e
            LEFT JOIN recognition_jobs j ON e.job_id = j.job_id
            WHERE j.job_id IS NULL
        """)
        orphaned_entities = cursor.fetchone()[0]
        
        if orphaned_entities == 0:
            print(f"[OK] No orphaned entities (all have valid job_id)")
        else:
            print(f"[WARNING] Found {orphaned_entities} orphaned entities!")
        
        # Check if entity counts match
        cursor.execute("""
            SELECT j.job_id, j.total_entities, COUNT(e.entity_id) as actual_count
            FROM recognition_jobs j
            LEFT JOIN entities e ON j.job_id = e.job_id
            WHERE j.job_id = ?
            GROUP BY j.job_id
        """, (job_id,))
        
        count_row = cursor.fetchone()
        if count_row:
            stored_count = count_row[1]
            actual_count = count_row[2]
            
            if stored_count == actual_count:
                print(f"[OK] Entity count matches (stored: {stored_count}, actual: {actual_count})")
            else:
                print(f"[ERROR] Entity count mismatch! (stored: {stored_count}, actual: {actual_count})")
        
    except sqlite3.Error as e:
        print(f"[ERROR] Integrity check failed: {e}")
    
    finally:
        conn.close()
    
    # Test 7: Database statistics
    print("\n[TEST 7] Database Statistics")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total jobs
        cursor.execute("SELECT COUNT(*) FROM recognition_jobs")
        total_jobs = cursor.fetchone()[0]
        print(f"Total recognition jobs: {total_jobs}")
        
        # Total entities
        cursor.execute("SELECT COUNT(*) FROM entities")
        total_entities = cursor.fetchone()[0]
        print(f"Total entities: {total_entities}")
        
        # Entities by type
        cursor.execute("""
            SELECT entity_type, COUNT(*) as count
            FROM entities
            GROUP BY entity_type
            ORDER BY count DESC
        """)
        entity_types = cursor.fetchall()
        
        print(f"\nEntities by type:")
        for entity_type, count in entity_types:
            print(f"  - {entity_type}: {count}")
        
        # Average confidence by type
        cursor.execute("""
            SELECT entity_type, AVG(confidence) as avg_conf
            FROM entities
            GROUP BY entity_type
            ORDER BY avg_conf DESC
        """)
        avg_confidences = cursor.fetchall()
        
        print(f"\nAverage confidence by type:")
        for entity_type, avg_conf in avg_confidences:
            print(f"  - {entity_type}: {avg_conf:.2f}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"[ERROR] Statistics query failed: {e}")
    
    print("\n" + "="*80)
    print("DATABASE TEST COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_database_storage()

# Made with Bob
