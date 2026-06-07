"""
Database manager for Vector Store module.
Uses unified database for better performance.
"""

from shared.unified_database import unified_db, ModuleDatabaseManager
from shared.config_loader import config
from modules.vector_store.models import Base, EmbeddingJob
from typing import Optional, List


class EmbeddingDatabaseManager(ModuleDatabaseManager[EmbeddingJob]):
    """
    Database manager for embedding generation jobs.
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
            model_class=EmbeddingJob
        )
        
        # Create tables
        unified_db.create_all_tables()
    
    def get_by_job_id(self, job_id: str) -> Optional[EmbeddingJob]:
        """
        Get embedding job by job_id.
        
        Args:
            job_id: Unique job identifier
        
        Returns:
            EmbeddingJob instance or None
        """
        with self.get_session() as session:
            job = session.query(EmbeddingJob).filter(
                EmbeddingJob.job_id == job_id
            ).first()
            if job:
                session.expunge(job)
            return job
    
    def get_by_model(
        self,
        model_name: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[EmbeddingJob]:
        """
        Get all jobs for a specific model.
        
        Args:
            model_name: Name of the embedding model
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of EmbeddingJob instances
        """
        with self.get_session() as session:
            query = session.query(EmbeddingJob).filter(
                EmbeddingJob.model_name == model_name
            ).order_by(EmbeddingJob.created_at.desc())
            
            if offset:
                query = query.offset(offset)
            
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            for job in results:
                session.expunge(job)
            return results
    
    def delete_by_job_id(self, job_id: str) -> bool:
        """
        Delete a job by job_id.
        
        Args:
            job_id: Unique job identifier
        
        Returns:
            True if deleted, False if not found
        """
        with self.get_session() as session:
            job = session.query(EmbeddingJob).filter(
                EmbeddingJob.job_id == job_id
            ).first()
            
            if job:
                session.delete(job)
                return True
            
            return False


# Create singleton instance
db = EmbeddingDatabaseManager()

# Made with Bob

