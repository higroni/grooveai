"""
Database manager for Entity Recognizer module.
"""

from shared.database_base import BaseDatabaseManager
from modules.entity_recognizer.models import Base, RecognitionJob


class EntityRecognizerDatabaseManager(BaseDatabaseManager[RecognitionJob]):
    """Database manager for entity recognition jobs."""
    
    def __init__(self, db_path: str = "data/databases/entity_recognizer.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        database_url = f"sqlite:///{db_path}"
        super().__init__(database_url=database_url, base_class=Base)


# Singleton instance
db = EntityRecognizerDatabaseManager()

# Made with Bob
