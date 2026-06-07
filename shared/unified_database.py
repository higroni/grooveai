"""
Unified Database Manager for GROOVE.AI
All modules use a single SQLite database with separate tables.
This improves performance by eliminating multiple database connections.
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


class UnifiedDatabaseManager:
    """
    Unified database manager for all GROOVE.AI modules.
    
    All modules share a single SQLite database instance with separate tables.
    This approach provides:
    - Better performance (single connection pool)
    - Easier backup and maintenance
    - Atomic transactions across modules
    - Reduced disk I/O
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, database_url: Optional[str] = None):
        """Singleton pattern - only one instance per database."""
        if cls._instance is None:
            cls._instance = super(UnifiedDatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        database_url: str = "sqlite:///data/databases/grooveai_unified.db",
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20
    ):
        """
        Initialize unified database manager.
        
        Args:
            database_url: SQLAlchemy database URL
            echo: Enable SQL query logging
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
        """
        # Only initialize once
        if self._initialized:
            return
            
        self.database_url = database_url
        self.logger = logging.getLogger(self.__class__.__name__)
        self._base_classes = []  # Track all registered base classes
        
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
        
        self._initialized = True
        self.logger.info(f"Unified database initialized: {database_url}")
    
    def _configure_sqlite(self):
        """Configure SQLite-specific optimizations."""
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            # Increase cache size (20MB)
            cursor.execute("PRAGMA cache_size=-20000")
            # Optimize for performance
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA mmap_size=30000000000")
            cursor.close()
    
    def register_base(self, base_class: Type[DeclarativeBase]):
        """
        Register a SQLAlchemy base class for table creation.
        
        Args:
            base_class: SQLAlchemy declarative base class
        """
        if base_class not in self._base_classes:
            self._base_classes.append(base_class)
            self.logger.info(f"Registered base class: {base_class.__name__}")
    
    def create_all_tables(self):
        """Create all tables for all registered base classes."""
        try:
            for base_class in self._base_classes:
                base_class.metadata.create_all(bind=self.engine)
                self.logger.info(f"Created tables for: {base_class.__name__}")
            self.logger.info("All database tables created successfully")
        except Exception as e:
            self.logger.error(f"Error creating tables: {e}", exc_info=True)
            raise
    
    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.
        
        Automatically commits on success, rolls back on error.
        
        Usage:
            with unified_db.get_session() as session:
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
    
    def close(self):
        """Close database connection and dispose engine."""
        self.engine.dispose()
        self.logger.info("Database connection closed")


class ModuleDatabaseManager(Generic[T]):
    """
    Module-specific database manager that uses the unified database.
    
    Each module creates an instance of this class with its own model type.
    All operations go through the shared unified database connection.
    """
    
    def __init__(
        self,
        unified_db: UnifiedDatabaseManager,
        base_class: Type[DeclarativeBase],
        model_class: Type[T]
    ):
        """
        Initialize module database manager.
        
        Args:
            unified_db: Shared unified database instance
            base_class: SQLAlchemy declarative base class
            model_class: Primary model class for this module
        """
        self.unified_db = unified_db
        self.base_class = base_class
        self.model_class = model_class
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{model_class.__name__}]")
        
        # Register base class with unified database
        self.unified_db.register_base(base_class)
    
    @contextmanager
    def get_session(self):
        """Get database session from unified database."""
        with self.unified_db.get_session() as session:
            yield session
    
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
    
    def get_by_id(self, obj_id: int) -> Optional[T]:
        """
        Get record by ID.
        
        Args:
            obj_id: Record ID
        
        Returns:
            Model instance or None
        """
        with self.get_session() as session:
            obj = session.query(self.model_class).filter(
                getattr(self.model_class, 'id') == obj_id
            ).first()
            if obj:
                session.expunge(obj)
            return obj
    
    def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """
        Get all records with optional pagination.
        
        Args:
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of model instances
        """
        with self.get_session() as session:
            query = session.query(self.model_class)
            
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
    
    def delete(self, obj_id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            obj_id: Record ID
        
        Returns:
            True if deleted, False if not found
        """
        with self.get_session() as session:
            obj = session.query(self.model_class).filter(
                getattr(self.model_class, 'id') == obj_id
            ).first()
            
            if obj:
                session.delete(obj)
                return True
            
            return False
    
    def count(self) -> int:
        """
        Count total records.
        
        Returns:
            Total record count
        """
        with self.get_session() as session:
            return session.query(self.model_class).count()


# Global unified database instance
unified_db = UnifiedDatabaseManager()


# Example usage
if __name__ == "__main__":
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
    from sqlalchemy import String, Integer
    
    # Define base
    class Base(DeclarativeBase):
        pass
    
    # Define model
    class TestModel(Base):
        __tablename__ = "test_table"
        
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        name: Mapped[str] = mapped_column(String(100))
        value: Mapped[int] = mapped_column(Integer)
    
    # Create unified database
    unified_db = UnifiedDatabaseManager(
        database_url="sqlite:///data/databases/test_unified.db"
    )
    
    # Create module database manager
    module_db = ModuleDatabaseManager(
        unified_db=unified_db,
        base_class=Base,
        model_class=TestModel
    )
    
    # Create tables
    unified_db.create_all_tables()
    
    # Test CRUD operations
    print("Testing unified database operations...")
    
    # Create
    obj = TestModel(name="test", value=42)
    created = module_db.create(obj)
    print(f"Created: {created.id}, {created.name}, {created.value}")
    
    # Read
    retrieved = module_db.get_by_id(created.id)
    if retrieved:
        print(f"Retrieved: {retrieved.id}, {retrieved.name}, {retrieved.value}")
        
        # Update
        retrieved.value = 100
        updated = module_db.update(retrieved)
        print(f"Updated: {updated.id}, {updated.name}, {updated.value}")
    
    # Count
    count = module_db.count()
    print(f"Total records: {count}")
    
    # Delete
    deleted = module_db.delete(created.id)
    print(f"Deleted: {deleted}")
    
    # Close
    unified_db.close()
    print("Unified database operations completed successfully")

# Made with Bob