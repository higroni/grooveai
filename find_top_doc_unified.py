import sqlite3
from pathlib import Path

db_path = Path("data/databases/grooveai_unified.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Simple approach - just count assertions per filename from legal_parser
cursor.execute("""
    SELECT 
        lpj.filename,
        lpj.total_units,
        COUNT(DISTINCT ej.id) as extraction_jobs,
        SUM(ej.total_assertions) as total_assertions
    FROM legal_parser_jobs lpj
    LEFT JOIN extraction_jobs ej ON ej.legal_unit_id IN (
        SELECT json_extract(value, '$.id')
        FROM legal_parser_jobs lpj2, json_each(lpj2.canonical_json)
        WHERE lpj2.id = lpj.id
    )
    WHERE lpj.filename LIKE '%.pdf'
    GROUP BY lpj.filename
    ORDER BY total_assertions DESC
    LIMIT 10
""")

print("Top 10 documents by assertions in UNIFIED DB:")
results = cursor.fetchall()
if results:
    for filename, units, jobs, total in results:
        print(f"  {filename}: {total} assertions, {units} units, {jobs} extraction jobs")
else:
    print("  No results - trying simpler query...")
    
    # Fallback - just show what we have
    cursor.execute("""
        SELECT filename, total_units, total_articles
        FROM legal_parser_jobs
        WHERE filename LIKE '%.pdf'
        ORDER BY total_units DESC
        LIMIT 10
    """)
    
    print("\nDocuments in legal_parser_jobs:")
    for filename, units, articles in cursor.fetchall():
        print(f"  {filename}: {units} units, {articles} articles")
    
    cursor.execute("SELECT COUNT(*) FROM extraction_jobs")
    print(f"\nTotal extraction_jobs: {cursor.fetchone()[0]}")

conn.close()

# Made with Bob
