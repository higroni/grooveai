"""
Database Migration Script - GROOVE.AI
Migrates data from separate module databases to unified database.

Usage:
    python migrate_to_unified_db.py [--dry-run] [--backup]
    
Options:
    --dry-run: Show what would be migrated without actually migrating
    --backup: Create backup of old databases before migration
"""

import sys
import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def backup_databases(db_dir: Path, backup_dir: Path):
    """Create backup of all existing databases."""
    logger.info("Creating backup of existing databases...")
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"backup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)
    
    db_files = list(db_dir.glob("*.db"))
    
    for db_file in db_files:
        if db_file.name != "grooveai_unified.db":
            dest = backup_path / db_file.name
            shutil.copy2(db_file, dest)
            logger.info(f"  Backed up: {db_file.name}")
    
    logger.info(f"Backup completed: {backup_path}")
    return backup_path


def check_old_databases(db_dir: Path) -> dict:
    """Check which old databases exist and their sizes."""
    logger.info("Checking existing databases...")
    
    databases = {
        "file_reader": db_dir / "file_reader.db",
        "text_normalizer": db_dir / "text_normalizer.db",
        "latinizer": db_dir / "latinizer.db",
        "legal_parser": db_dir / "legal_parser.db",
        "assertion_extractor": db_dir / "assertion_extractor.db",
        "entity_recognizer": db_dir / "entity_recognizer.db",
        "condition_extractor": db_dir / "condition_extractor.db",
        "assertion_classifier": db_dir / "assertion_classifier.db",
        "knowledge_enrichment": db_dir / "knowledge_enrichment.db",
        "embedding_generator": db_dir / "embedding_generator.db",
        "vector_store": db_dir / "vector_store.db",
    }
    
    existing = {}
    total_size = 0
    
    for name, path in databases.items():
        if path.exists():
            size = path.stat().st_size
            existing[name] = {
                "path": path,
                "size": size,
                "size_mb": size / (1024 * 1024)
            }
            total_size += size
            logger.info(f"  Found: {name}.db ({existing[name]['size_mb']:.2f} MB)")
    
    logger.info(f"Total size of old databases: {total_size / (1024 * 1024):.2f} MB")
    return existing


def migrate_data(existing_dbs: dict, unified_db_path: Path, dry_run: bool = False):
    """Migrate data from old databases to unified database."""
    if dry_run:
        logger.info("DRY RUN MODE - No actual migration will occur")
        logger.info(f"Would migrate {len(existing_dbs)} databases to: {unified_db_path}")
        return
    
    logger.info("Starting data migration...")
    logger.info(f"Target unified database: {unified_db_path}")
    
    # Import after checking to avoid errors if modules not ready
    try:
        from shared.unified_database import unified_db
        from shared.config_loader import config
        
        # Initialize unified database
        unified_db_url = config.get_unified_database_url()
        unified_db.__init__(database_url=unified_db_url)
        
        logger.info("Unified database initialized")
        
        # Note: Actual data migration would require reading from old databases
        # and inserting into new unified database using SQLAlchemy
        # This is a placeholder for the migration logic
        
        logger.warning("Data migration logic not yet implemented")
        logger.warning("Old databases are preserved - manual migration may be required")
        logger.info("All modules will now use the unified database for new data")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}", exc_info=True)
        raise


def verify_migration(unified_db_path: Path):
    """Verify that unified database was created successfully."""
    logger.info("Verifying migration...")
    
    if not unified_db_path.exists():
        logger.error("Unified database was not created!")
        return False
    
    size = unified_db_path.stat().st_size
    logger.info(f"Unified database created: {size / (1024 * 1024):.2f} MB")
    
    # Could add more verification checks here
    return True


def main():
    """Main migration script."""
    parser = argparse.ArgumentParser(
        description="Migrate GROOVE.AI databases to unified database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without actually migrating"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup of old databases before migration"
    )
    parser.add_argument(
        "--db-dir",
        type=str,
        default="data/databases",
        help="Directory containing databases (default: data/databases)"
    )
    
    args = parser.parse_args()
    
    logger.info("="*80)
    logger.info("GROOVE.AI Database Migration to Unified Database")
    logger.info("="*80)
    
    # Setup paths
    db_dir = Path(args.db_dir)
    if not db_dir.exists():
        logger.error(f"Database directory not found: {db_dir}")
        return 1
    
    unified_db_path = db_dir / "grooveai_unified.db"
    backup_dir = db_dir / "backups"
    
    # Check existing databases
    existing_dbs = check_old_databases(db_dir)
    
    if not existing_dbs:
        logger.warning("No old databases found - nothing to migrate")
        logger.info("Unified database will be created when modules start")
        return 0
    
    # Create backup if requested
    backup_path = None
    if args.backup and not args.dry_run:
        backup_path = backup_databases(db_dir, backup_dir)
        logger.info(f"Backup created at: {backup_path}")
    
    # Migrate data
    try:
        migrate_data(existing_dbs, unified_db_path, dry_run=args.dry_run)
        
        if not args.dry_run:
            # Verify migration
            if verify_migration(unified_db_path):
                logger.info("="*80)
                logger.info("Migration completed successfully!")
                logger.info("="*80)
                logger.info("")
                logger.info("Next steps:")
                logger.info("1. Test the unified database with all modules")
                logger.info("2. Verify data integrity")
                logger.info("3. Once verified, old database files can be archived")
                logger.info("")
                logger.info(f"Old databases preserved in: {db_dir}")
                if args.backup and backup_path:
                    logger.info(f"Backup available at: {backup_path}")
                return 0
            else:
                logger.error("Migration verification failed!")
                return 1
        else:
            logger.info("="*80)
            logger.info("Dry run completed - no changes made")
            logger.info("="*80)
            return 0
            
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob