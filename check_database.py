"""
Check File Reader database contents
"""
import sqlite3
import os
from datetime import datetime

# Database path from config
db_path = "data/databases/file_reader.db"

print("=" * 80)
print("FILE READER DATABASE CHECK")
print("=" * 80)

# Check if database exists
if not os.path.exists(db_path):
    print(f"\nERROR: Database not found at: {db_path}")
    exit(1)

print(f"\nDatabase: {db_path}")
print(f"Size: {os.path.getsize(db_path)} bytes")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table info
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"\nTables: {[t[0] for t in tables]}")

# Get all jobs
cursor.execute("SELECT * FROM file_reader_jobs ORDER BY created_at DESC")
jobs = cursor.fetchall()

print(f"\nTotal jobs in database: {len(jobs)}")
print("\n" + "=" * 80)

if jobs:
    # Get column names
    cursor.execute("PRAGMA table_info(file_reader_jobs)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"Columns: {', '.join(columns)}")
    print("=" * 80)
    
    # Display each job
    for i, job in enumerate(jobs, 1):
        print(f"\nJob #{i}:")
        print("-" * 80)
        for col_name, value in zip(columns, job):
            if col_name == 'output_text' and value:
                # Show text statistics instead of full text
                print(f"  {col_name}: {len(value)} characters (stored in database)")
                # Don't print actual text to avoid encoding issues
            else:
                print(f"  {col_name}: {value}")
    
    # Check if latest job has output_text
    latest_job = jobs[0]
    output_text_index = columns.index('output_text')
    output_text = latest_job[output_text_index]
    
    print("\n" + "=" * 80)
    print("LATEST JOB VERIFICATION")
    print("=" * 80)
    
    if output_text:
        print(f"Output text stored: YES")
        print(f"Length: {len(output_text)} characters")
        print(f"Contains Cyrillic: {'Yes' if any(ord(c) >= 0x0400 and ord(c) <= 0x04FF for c in output_text[:1000]) else 'No'}")
        
        # Save to file for inspection
        with open("database_output_text.txt", "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"\nOutput text saved to: database_output_text.txt")
    else:
        print(f"Output text stored: NO")
        print("WARNING: output_text is NULL or empty!")
else:
    print("\nNo jobs found in database.")

conn.close()

print("\n" + "=" * 80)
print("DATABASE CHECK COMPLETE")
print("=" * 80)

# Made with Bob
