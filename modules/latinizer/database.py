"""
Database manager for Latinizer module.

This module provides database operations for latinization jobs.
Uses the shared BaseDatabaseManager for common functionality.
"""

from shared.database_base import BaseDatabaseManager
from shared.config_loader import config
from modules.latinizer.models import Base, LatinizerJob
from typing import Optional, List


class LatinizerDatabaseManager(BaseDatabaseManager[LatinizerJob]):
    """
    Database manager for latinization jobs.
    
    Extends BaseDatabaseManager with latinizer-specific operations.
    """
    
    def __init__(self):
        """Initialize database manager with module-specific configuration."""
        db_url = config.get_database_url("latinizer")
        super().__init__(db_url, Base)
    


# Create singleton instance
db = LatinizerDatabaseManager()

# Made with Bob
