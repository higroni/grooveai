import sqlite3
from pathlib import Path

db_path = Path("data/databases/grooveai_unified.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find documents with most assertions
cursor.execute("""
    SELECT 
        frj.file_path,
        COUNT(DISTINCT ej.id) as assertion_count,
        SUM(ej.total_assertions) as total_assertions
    FROM file_reader_jobs frj
    LEFT JOIN extraction_jobs ej ON frj.job_id = ej.job_id
    WHERE ej.id IS NOT NULL
    GROUP BY frj.file_path
    ORDER BY total_assertions DESC
    LIMIT 10
""")

print("Top 10 documents by assertion count in UNIFIED DB:")
for file_path, job_count, total in cursor.fetchall():
    print(f"  {Path(file_path).name}: {total} assertions ({job_count} extraction jobs)")

conn.close()

# Made with Bob
