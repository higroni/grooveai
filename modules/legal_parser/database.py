"""Database operations for Legal Parser module.
Uses unified database for better performance."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.unified_database import unified_db, ModuleDatabaseManager
from shared.config_loader import config
from modules.legal_parser.models import Base, LegalParserJob


class LegalParserDatabaseManager(ModuleDatabaseManager[LegalParserJob]):
    """Database manager for Legal Parser jobs.
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
            model_class=LegalParserJob
        )
        
        # Create tables
        unified_db.create_all_tables()


# Singleton instance
db = LegalParserDatabaseManager()

# Made with Bob
