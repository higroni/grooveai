"""Database operations for Assertion Extractor module."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database_base import BaseDatabaseManager
from modules.assertion_extractor.models import Base, ExtractionJob


class AssertionExtractorDatabaseManager(BaseDatabaseManager[ExtractionJob]):
    """Database manager for Assertion Extractor jobs."""
    
    def __init__(self, db_path: str = "data/databases/assertion_extractor.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        database_url = f"sqlite:///{db_path}"
        super().__init__(
            database_url=database_url,
            base_class=Base
        )


# Singleton instance
db = AssertionExtractorDatabaseManager()

# Made with Bob
