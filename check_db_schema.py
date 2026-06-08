"""
Check database schema to see actual column names.
"""

import sqlite3
import sys
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

db_path = Path("data/databases/grooveai_unified.db")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print("="*80)
print("DATABASE SCHEMA")
print("="*80)

for table in tables:
    print(f"\n{table}:")
    print("-" * 40)
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    for col in columns:
        col_id, name, col_type, not_null, default, pk = col
        print(f"  {name} ({col_type}){' PRIMARY KEY' if pk else ''}{' NOT NULL' if not_null else ''}")
    
    # Show row count
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  -> {count} rows")

conn.close()

# Made with Bob
