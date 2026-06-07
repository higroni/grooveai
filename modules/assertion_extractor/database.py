"""Database operations for Assertion Extractor module.
Uses unified database for better performance."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.unified_database import unified_db, ModuleDatabaseManager
from shared.config_loader import config
from modules.assertion_extractor.models import Base, ExtractionJob


class AssertionExtractorDatabaseManager(ModuleDatabaseManager[ExtractionJob]):
    """Database manager for Assertion Extractor jobs.
    Uses the unified database instance."""
    
    def __init__(self):
        """Initialize database manager with unified database."""
        # Initialize unified database with config
        unified_db_url = config.get_unified_database_url()
        unified_db.__init__(database_url=unified_db_url)
        
        # Initialize module database manager
        super().__init__(
            unified_db=unified_db,
            base_class=Base,
            model_class=ExtractionJob
        )
        
        # Create tables
        unified_db.create_all_tables()


# Singleton instance
db = AssertionExtractorDatabaseManager()

# Made with Bob
