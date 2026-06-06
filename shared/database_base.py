"""
Shared database utilities for all GROOVE.AI modules.

This module provides:
- Base database manager class
- Common database operations
- Session management with context managers
- Standardized error handling
- Connection pooling configuration
"""

from contextlib import contextmanager
from typing import Optional, Type, TypeVar, Generic, List
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import StaticPool
from pathlib import Path
import logging

# Type variable for generic model operations
T = TypeVar('T', bound=DeclarativeBase)


class BaseDatabaseManager(Generic[T]):
    """
    Base database manager for GROOVE.AI modules.
    
    Provides:
    - Session management with context managers
    - Common CRUD operations
    - Connection pooling
    - SQLite optimization (WAL mode, foreign keys)
    - Automatic table creation
    
    Usage:
        class MyDatabaseManager(BaseDatabaseManager):
            def __init__(self, db_url: str):
                super().__init__(db_url, MyBase)
    """
    
    def __init__(
        self,
        database_url: str,
        base_class: Type[DeclarativeBase],
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10
    ):
        """
        Initialize database manager.
        
        Args:
            database_url: SQLAlchemy database URL
            base_class: SQLAlchemy declarative base class
            echo: Enable SQL query logging
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
        """
        self.database_url = database_url
        self.base_class = base_class
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Create database directory if using SQLite
        if database_url.startswith('sqlite:///'):
            db_path = database_url.replace('sqlite:///', '')
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Configure engine based on database type
        if database_url.startswith('sqlite:'):
            # SQLite-specific configuration
            self.engine = create_engine(
                database_url,
                echo=echo,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
            
            # Enable SQLite optimizations
            self._configure_sqlite()
        else:
            # PostgreSQL/MySQL configuration
            self.engine = create_engine(
                database_url,
                echo=echo,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=True  # Verify connections before using
            )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create tables
        self.create_tables()
    
    def _configure_sqlite(self):
        """Configure SQLite-specific optimizations."""
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            # Increase cache size (10MB)
            cursor.execute("PRAGMA cache_size=-10000")
            cursor.close()
    
    def create_tables(self):
        """Create all tables defined in the base class."""
        try:
            self.base_class.metadata.create_all(bind=self.engine)
            self.logger.info("Database tables created successfully")
        except Exception as e:
            self.logger.error(f"Error creating tables: {e}", exc_info=True)
            raise
    
    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.
        
        Automatically commits on success, rolls back on error.
        
        Usage:
            with db.get_session() as session:
                session.add(obj)
                # Automatic commit on exit
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            session.close()
    
    def create(self, obj: T) -> T:
        """
        Create a new record.
        
        Args:
            obj: SQLAlchemy model instance
        
        Returns:
            Created object with ID populated
        """
        with self.get_session() as session:
            session.add(obj)
            session.flush()
            session.refresh(obj)
            # Make object accessible after session closes
            session.expunge(obj)
            return obj
    
    def get_by_id(self, model_class: Type[T], obj_id: int) -> Optional[T]:
        """
        Get record by ID.
        
        Args:
            model_class: SQLAlchemy model class
            obj_id: Record ID
        
        Returns:
            Model instance or None
        """
        with self.get_session() as session:
            obj = session.query(model_class).filter(
                model_class.id == obj_id
            ).first()
            if obj:
                session.expunge(obj)
            return obj
    
    def get_all(
        self,
        model_class: Type[T],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """
        Get all records with optional pagination.
        
        Args:
            model_class: SQLAlchemy model class
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of model instances
        """
        with self.get_session() as session:
            query = session.query(model_class)
            
            if offset:
                query = query.offset(offset)
            
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            # Expunge all objects to make them accessible after session closes
            for obj in results:
                session.expunge(obj)
            return results
    
    def update(self, obj: T) -> T:
        """
        Update an existing record.
        
        Args:
            obj: SQLAlchemy model instance with updated values
        
        Returns:
            Updated object
        """
        with self.get_session() as session:
            merged = session.merge(obj)
            session.flush()
            session.refresh(merged)
            session.expunge(merged)
            return merged
    
    def delete(self, model_class: Type[T], obj_id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            model_class: SQLAlchemy model class
            obj_id: Record ID
        
        Returns:
            True if deleted, False if not found
        """
        with self.get_session() as session:
            obj = session.query(model_class).filter(
                model_class.id == obj_id
            ).first()
            
            if obj:
                session.delete(obj)
                return True
            
            return False
    
    def count(self, model_class: Type[T]) -> int:
        """
        Count total records.
        
        Args:
            model_class: SQLAlchemy model class
        
        Returns:
            Total record count
        """
        with self.get_session() as session:
            return session.query(model_class).count()
    
    def close(self):
        """Close database connection and dispose engine."""
        self.engine.dispose()
        self.logger.info("Database connection closed")


# Example usage
if __name__ == "__main__":
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
    from sqlalchemy import String, Integer
    from datetime import datetime
    
    # Define base
    class Base(DeclarativeBase):
        pass
    
    # Define model
    class TestModel(Base):
        __tablename__ = "test_table"
        
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        name: Mapped[str] = mapped_column(String(100))
        value: Mapped[int] = mapped_column(Integer)
    
    # Create database manager
    db = BaseDatabaseManager(
        database_url="sqlite:///data/databases/test.db",
        base_class=Base
    )
    
    # Test CRUD operations
    print("Testing database operations...")
    
    # Create
    obj = TestModel(name="test", value=42)
    created = db.create(obj)
    print(f"Created: {created.id}, {created.name}, {created.value}")
    
    # Read
    retrieved = db.get_by_id(TestModel, created.id)
    print(f"Retrieved: {retrieved.id}, {retrieved.name}, {retrieved.value}")
    
    # Update
    retrieved.value = 100
    updated = db.update(retrieved)
    print(f"Updated: {updated.id}, {updated.name}, {updated.value}")
    
    # Count
    count = db.count(TestModel)
    print(f"Total records: {count}")
    
    # Delete
    deleted = db.delete(TestModel, created.id)
    print(f"Deleted: {deleted}")
    
    # Close
    db.close()
    print("Database operations completed successfully")

# Made with Bob
