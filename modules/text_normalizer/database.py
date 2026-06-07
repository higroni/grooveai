"""
Database management for Text Normalizer module
Uses unified database for better performance
"""
from shared.unified_database import unified_db, ModuleDatabaseManager
from shared.config_loader import config
from modules.text_normalizer.models import Base, TextNormalizerJob


class TextNormalizerDatabaseManager(ModuleDatabaseManager[TextNormalizerJob]):
    """
    Database manager for Text Normalizer module.
    Uses the unified database instance.
    """
    
    def __init__(self):
        """Initialize database manager with unified database."""
        # Initialize unified database with config
        unified_db_url = config.get_unified_database_url()
        unified_db.__init__(database_url=unified_db_url)
        
        # Initialize module database manager
        super().__init__(
            unified_db=unified_db,
            base_class=Base,
            model_class=TextNormalizerJob
        )
        
        # Create tables
        unified_db.create_all_tables()


# Global database instance
db = TextNormalizerDatabaseManager()

# Made with Bob
