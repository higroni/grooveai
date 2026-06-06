"""Check Latinizer database contents."""

import sys
import os
import sqlite3

# Setup UTF-8 encoding for Windows terminal
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def check_database():
    """Check what's stored in the latinizer database."""
    
    conn = sqlite3.connect('data/databases/latinizer.db')
    cursor = conn.cursor()
    
    # Get the latest job
    cursor.execute('''
        SELECT id, length(input_text), length(output_text), 
               cyrillic_chars_converted, processing_time_ms, created_at
        FROM latinizer_jobs 
        ORDER BY id DESC 
        LIMIT 1
    ''')
    
    row = cursor.fetchone()
    
    if row:
        print("=" * 80)
        print("LATEST LATINIZER JOB IN DATABASE")
        print("=" * 80)
        print(f"Job ID: {row[0]}")
        print(f"Input text length: {row[1]} characters")
        print(f"Output text length: {row[2]} characters")
        print(f"Cyrillic chars converted: {row[3]}")
        print(f"Processing time: {row[4]}ms")
        print(f"Created at: {row[5]}")
        print("=" * 80)
        
        # Get a sample of the input and output
        cursor.execute('''
            SELECT substr(input_text, 1, 200), substr(output_text, 1, 200)
            FROM latinizer_jobs 
            WHERE id = ?
        ''', (row[0],))
        
        sample = cursor.fetchone()
        print("\nINPUT SAMPLE (first 200 chars):")
        print(sample[0])
        print("\nOUTPUT SAMPLE (first 200 chars):")
        print(sample[1])
        print("=" * 80)
        
        # Count total jobs
        cursor.execute('SELECT COUNT(*) FROM latinizer_jobs')
        total = cursor.fetchone()[0]
        print(f"\nTotal jobs in database: {total}")
        
    else:
        print("No jobs found in database!")
    
    conn.close()

if __name__ == "__main__":
    check_database()

# Made with Bob
