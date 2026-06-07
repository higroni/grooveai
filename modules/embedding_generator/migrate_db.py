"""
Database migration script for Embedding Generator module.
Adds new columns for hybrid embedding strategy support.
"""

import sqlite3
import sys
from pathlib import Path

def migrate_database():
    """Add new columns to existing embedding_jobs table."""
    
    # Database path
    db_path = Path(__file__).parent / "embedding_generator.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        print("No migration needed - new database will be created with correct schema.")
        return
    
    print(f"Migrating database: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(embedding_jobs)")
        columns = {row[1] for row in cursor.fetchall()}
        
        migrations = []
        
        # Add embedding_type column
        if 'embedding_type' not in columns:
            migrations.append(
                "ALTER TABLE embedding_jobs ADD COLUMN embedding_type VARCHAR(20) DEFAULT 'document'"
            )
            print("  - Adding embedding_type column")
        
        # Add embedding_metadata column
        if 'embedding_metadata' not in columns:
            migrations.append(
                "ALTER TABLE embedding_jobs ADD COLUMN embedding_metadata TEXT"
            )
            print("  - Adding embedding_metadata column")
        
        # Add assertion_type column
        if 'assertion_type' not in columns:
            migrations.append(
                "ALTER TABLE embedding_jobs ADD COLUMN assertion_type VARCHAR(50)"
            )
            print("  - Adding assertion_type column")
        
        # Add assertion_id column
        if 'assertion_id' not in columns:
            migrations.append(
                "ALTER TABLE embedding_jobs ADD COLUMN assertion_id VARCHAR(100)"
            )
            print("  - Adding assertion_id column")
        
        # Add source_document column
        if 'source_document' not in columns:
            migrations.append(
                "ALTER TABLE embedding_jobs ADD COLUMN source_document VARCHAR(500)"
            )
            print("  - Adding source_document column")
        
        # Add source_article column
        if 'source_article' not in columns:
            migrations.append(
                "ALTER TABLE embedding_jobs ADD COLUMN source_article VARCHAR(100)"
            )
            print("  - Adding source_article column")
        
        # Execute migrations
        if migrations:
            for migration in migrations:
                cursor.execute(migration)
            
            conn.commit()
            print(f"\n✓ Migration completed successfully! Added {len(migrations)} columns.")
        else:
            print("\n✓ Database schema is already up to date. No migration needed.")
        
        # Create indexes
        print("\nCreating indexes...")
        try:
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_embedding_type ON embedding_jobs(embedding_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_assertion_type ON embedding_jobs(assertion_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_assertion_id ON embedding_jobs(assertion_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_source_article ON embedding_jobs(source_article)"
            )
            conn.commit()
            print("✓ Indexes created successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not create indexes: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()

# Made with Bob
