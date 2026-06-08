import sqlite3
from pathlib import Path

db_path = Path("data/databases/grooveai_unified.db")

if not db_path.exists():
    print(f"ERROR: Unified database does not exist: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]

print(f"Unified DB has {len(tables)} tables:")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table}: {count} rows")

print("\n" + "="*60)
print("CHECKING MODULE DATABASE CONFIGURATIONS")
print("="*60)

# Check which modules are configured to use unified DB
modules_to_check = [
    "file_reader",
    "text_normalizer", 
    "latinizer",
    "legal_parser",
    "assertion_extractor",
    "entity_recognizer",
    "condition_extractor",
    "assertion_classifier",
    "embedding_generator",
    "vector_store"
]

for module in modules_to_check:
    db_file = Path(f"modules/{module}/database.py")
    if db_file.exists():
        content = db_file.read_text(encoding='utf-8')
        if "grooveai_unified.db" in content:
            print(f"[OK] {module}: USING unified DB")
        else:
            print(f"[X] {module}: NOT using unified DB")
    else:
        print(f"? {module}: database.py not found")

conn.close()

# Made with Bob
