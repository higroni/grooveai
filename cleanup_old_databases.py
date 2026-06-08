"""
Cleanup script for old individual module databases.
All modules now use the unified database (grooveai_unified.db).
This script backs up and removes old individual database files.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Database directory
DB_DIR = Path("data/databases")
BACKUP_DIR = Path("data/database_backups")

# Old databases to remove (all modules now use unified database)
OLD_DATABASES = [
    "assertion_classifier.db",
    "assertion_extractor.db",
    "condition_extractor.db",
    "embedding_generator.db",
    "entity_recognizer.db",
    "file_reader.db",
    "knowledge_enrichment.db",
    "latinizer.db",
    "legal_parser.db",
    "text_normalizer.db",
    "test.db"
]

def create_backup():
    """Create backup of old databases before deletion."""
    print("=" * 80)
    print("DATABASE CLEANUP - BACKUP & REMOVAL")
    print("=" * 80)
    print()
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"backup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)
    
    print(f"[BACKUP] Creating backup in: {backup_path}")
    print()
    
    total_size = 0
    backed_up = 0
    
    for db_file in OLD_DATABASES:
        db_path = DB_DIR / db_file
        if db_path.exists():
            # Get file size
            size_mb = db_path.stat().st_size / (1024 * 1024)
            total_size += size_mb
            
            # Copy to backup
            backup_file = backup_path / db_file
            shutil.copy2(db_path, backup_file)
            backed_up += 1
            
            print(f"  [OK] Backed up: {db_file} ({size_mb:.2f} MB)")
        else:
            print(f"  [WARN] Not found: {db_file}")
    
    print()
    print(f"[SUMMARY] Backup Summary:")
    print(f"   Files backed up: {backed_up}/{len(OLD_DATABASES)}")
    print(f"   Total size: {total_size:.2f} MB")
    print(f"   Backup location: {backup_path}")
    print()
    
    return backup_path, backed_up, total_size

def remove_old_databases():
    """Remove old database files."""
    print("[CLEANUP] Removing old database files...")
    print()
    
    removed = 0
    freed_space = 0
    
    for db_file in OLD_DATABASES:
        db_path = DB_DIR / db_file
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            freed_space += size_mb
            
            # Remove file
            db_path.unlink()
            removed += 1
            
            print(f"  [OK] Removed: {db_file} ({size_mb:.2f} MB)")
        else:
            print(f"  [WARN] Already removed: {db_file}")
    
    print()
    print(f"[SUMMARY] Cleanup Summary:")
    print(f"   Files removed: {removed}/{len(OLD_DATABASES)}")
    print(f"   Space freed: {freed_space:.2f} MB")
    print()
    
    return removed, freed_space

def verify_unified_database():
    """Verify that unified database exists and is being used."""
    print("[VERIFY] Checking unified database...")
    print()
    
    unified_db = DB_DIR / "grooveai_unified.db"
    
    if unified_db.exists():
        size_mb = unified_db.stat().st_size / (1024 * 1024)
        modified = datetime.fromtimestamp(unified_db.stat().st_mtime)
        
        print(f"  [OK] Unified database found:")
        print(f"     Path: {unified_db}")
        print(f"     Size: {size_mb:.2f} MB")
        print(f"     Last modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        return True
    else:
        print(f"  [ERROR] Unified database not found!")
        print(f"     Expected: {unified_db}")
        print()
        return False

def main():
    """Main cleanup process."""
    # Verify unified database exists
    if not verify_unified_database():
        print("❌ Cannot proceed without unified database!")
        return
    
    # Create backup
    backup_path, backed_up, backup_size = create_backup()
    
    if backed_up == 0:
        print("[INFO] No old databases found to clean up.")
        return
    
    # Ask for confirmation
    print("[WARNING] This will permanently delete old database files!")
    print("   (Backup has been created)")
    print()
    response = input("Continue with cleanup? (yes/no): ").strip().lower()
    
    if response != "yes":
        print()
        print("[CANCELLED] Cleanup cancelled.")
        print(f"   Backup remains at: {backup_path}")
        return
    
    print()
    
    # Remove old databases
    removed, freed_space = remove_old_databases()
    
    # Final summary
    print("=" * 80)
    print("[SUCCESS] DATABASE CONSOLIDATION COMPLETE")
    print("=" * 80)
    print()
    print(f"[BACKUP] Backup created: {backup_path}")
    print(f"[CLEANUP] Files removed: {removed}")
    print(f"[SPACE] Space freed: {freed_space:.2f} MB")
    print(f"[DATABASE] Unified database: data/databases/grooveai_unified.db")
    print()
    print("All modules now use a single unified database for better performance!")
    print("=" * 80)

if __name__ == "__main__":
    main()

# Made with Bob
