"""
Script to check the unified database structure and contents.
"""
import sqlite3
import os
from pathlib import Path
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def check_unified_database():
    """Check the unified database structure."""
    db_path = Path("data/databases/grooveai_unified.db")
    
    if not db_path.exists():
        print(f"[X] Unified database not found at: {db_path}")
        print("\nExpected location: data/databases/grooveai_unified.db")
        return
    
    print(f"[OK] Unified database found at: {db_path}")
    print(f"     Size: {db_path.stat().st_size / 1024:.2f} KB\n")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"[INFO] Found {len(tables)} tables:\n")
    
    for (table_name,) in tables:
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"  TABLE: {table_name}")
        print(f"     Rows: {count}")
        print(f"     Columns: {len(columns)}")
        
        # Show column details
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            pk_marker = " [PK]" if pk else ""
            not_null_marker = " NOT NULL" if not_null else ""
            print(f"       - {col_name}: {col_type}{pk_marker}{not_null_marker}")
        
        print()
    
    conn.close()
    
    print("\n" + "="*60)
    print("Database check complete!")
    print("="*60)

if __name__ == "__main__":
    check_unified_database()

# Made with Bob
