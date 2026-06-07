"""
Database manager for Vector Store module.

This module provides database operations for embedding generation jobs.
Uses the shared BaseDatabaseManager for common functionality.
"""

from shared.database_base import BaseDatabaseManager
from shared.config_loader import config
from modules.vector_store.models import Base, EmbeddingJob
from typing import Optional, List


class EmbeddingDatabaseManager(BaseDatabaseManager[EmbeddingJob]):
    """
    Database manager for embedding generation jobs.
    
    Extends BaseDatabaseManager with embedding-specific operations.
    """
    
    def __init__(self):
        """Initialize database manager with module-specific configuration."""
        db_url = config.get_database_url("vector_store")
        super().__init__(db_url, Base)
    
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

