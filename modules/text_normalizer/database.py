"""
Database management for Text Normalizer module
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from modules.text_normalizer.models import Base
from shared.config_loader import config


class Database:
    """
    Database manager for Text Normalizer module
    """
    
    def __init__(self):
        """Initialize database connection"""
        self.database_url = config.get_database_url("text_normalizer")
        
        # Ensure directory exists for SQLite
        if self.database_url.startswith("sqlite:///"):
            db_path = self.database_url.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.engine = create_engine(
            self.database_url,
            echo=config.get("database.echo", False)
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables
        self.create_tables()
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session with automatic cleanup
        
        Usage:
            with db.get_session() as session:
                # use session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database instance
db = Database()

# Made with Bob
