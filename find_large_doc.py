import sqlite3
from pathlib import Path

# Check unified database
db_path = Path("data/databases/grooveai_unified.db")

if db_path.exists():
    print(f"Checking unified database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # First check schema
    cursor.execute("PRAGMA table_info(file_reader_jobs)")
    columns = cursor.fetchall()
    print("\nfile_reader_jobs columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    cursor.execute("PRAGMA table_info(extraction_jobs)")
    columns = cursor.fetchall()
    print("\nextraction_jobs columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Find documents with most assertions
    # Note: extraction_jobs.job_id links to file_reader_jobs.job_id
    cursor.execute("""
        SELECT
            frj.file_path,
            SUM(ej.total_assertions) as total_assertions,
            COUNT(ej.id) as extraction_job_count
        FROM file_reader_jobs frj
        LEFT JOIN extraction_jobs ej ON frj.job_id = ej.job_id
        WHERE ej.id IS NOT NULL
        GROUP BY frj.file_path
        ORDER BY total_assertions DESC
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    print("\nTop 10 documents by assertion count (unified DB):")
    for filename, total, job_count in results:
        print(f"  {filename}: {total} assertions ({job_count} extraction jobs)")
    
    conn.close()
else:
    print(f"Unified database not found: {db_path}")

# Check old assertion_extractor database
old_db_path = Path("data/databases/assertion_extractor.db")
if old_db_path.exists():
    print(f"\nChecking old database: {old_db_path}")
    conn = sqlite3.connect(old_db_path)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")
    
    # Check schema first
    cursor.execute("PRAGMA table_info(extraction_jobs)")
    columns = cursor.fetchall()
    print(f"extraction_jobs columns: {[col[1] for col in columns]}")
    
    # Count total assertions
    cursor.execute("SELECT SUM(total_assertions), COUNT(*) FROM extraction_jobs")
    total, count = cursor.fetchone()
    print(f"\nTotal: {total} assertions across {count} extraction jobs")
    
    # Show sample
    cursor.execute("SELECT job_id, legal_unit_id, total_assertions FROM extraction_jobs LIMIT 5")
    print("\nSample extraction jobs:")
    for job_id, unit_id, assertions in cursor.fetchall():
        print(f"  {job_id[:8]}... unit={unit_id[:20]}... assertions={assertions}")
    
    conn.close()
else:
    print(f"Old database not found: {old_db_path}")

# Check legal_parser database
parser_db_path = Path("data/databases/legal_parser.db")
if parser_db_path.exists():
    print(f"\nChecking parser database: {parser_db_path}")
    conn = sqlite3.connect(parser_db_path)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")
    
    # Check schema
    cursor.execute("PRAGMA table_info(legal_parser_jobs)")
    columns = cursor.fetchall()
    print(f"legal_parser_jobs columns: {[col[1] for col in columns]}")
    
    # Check for documents
    cursor.execute("""
        SELECT
            filename,
            total_units,
            total_articles,
            total_paragraphs,
            document_title
        FROM legal_parser_jobs
        ORDER BY total_units DESC
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    print("\nTop 10 documents by legal unit count:")
    for filename, units, articles, paragraphs, title in results:
        print(f"  {filename}: {units} units, {articles} articles, {paragraphs} paragraphs")
        print(f"    Title: {title[:60]}...")
        
        # If this looks like the big document (800+ assertions likely means 100+ units)
        if units and units > 100:
            print(f"    -> This is likely the large document!")
    
    conn.close()

# Made with Bob
