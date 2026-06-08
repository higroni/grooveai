import sqlite3

conn = sqlite3.connect('data/databases/grooveai_unified.db')
cursor = conn.cursor()

# Find documents with assertions
cursor.execute("""
    SELECT f.job_id, f.file_path, COUNT(e.id) as assertion_count
    FROM file_reader_jobs f
    LEFT JOIN extraction_jobs e ON e.job_id LIKE f.job_id || '%'
    WHERE f.status = 'success'
    GROUP BY f.job_id, f.file_path
    HAVING assertion_count > 0
    LIMIT 5
""")

print("Documents with assertions:")
for row in cursor.fetchall():
    print(f"  {row[0][:20]}... -> {row[2]} assertions")
    print(f"    File: {row[1]}")
    print()

conn.close()

# Made with Bob
