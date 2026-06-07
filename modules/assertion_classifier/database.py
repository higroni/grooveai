"""
Database operations for Assertion Classifier module.
"""

import json
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from modules.assertion_classifier.models import (
    Base,
    ClassificationJobDB,
    ClassificationStatsDB,
    ClassificationOutput
)


class ClassificationDatabase:
    """Database manager for assertion classification."""
    
    def __init__(self, db_url: str = "sqlite:///data/databases/assertion_classifier.db"):
        """
        Initialize database connection.
        
        Args:
            db_url: Database URL (default: SQLite)
        """
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
    
    def save_classification(
        self,
        job_id: str,
        output: ClassificationOutput,
        language: str,
        processing_time_ms: int
    ) -> ClassificationJobDB:
        """
        Save classification result to database.
        
        Args:
            job_id: Unique job ID
            output: Classification output
            language: Language code
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            Saved ClassificationJobDB instance
        """
        with Session(self.engine) as session:
            classification = output.classification
            
            # Create job record
            job = ClassificationJobDB(
                job_id=job_id,
                assertion_id=classification.assertion_id,
                assertion_text="",  # Will be updated if needed
                assertion_type=classification.assertion_type,
                confidence=classification.confidence,
                matched_patterns=json.dumps(classification.matched_patterns),
                reasoning=classification.reasoning,
                language=language,
                processing_time_ms=processing_time_ms
            )
            
            session.add(job)
            session.commit()
            session.refresh(job)
            
            # Update statistics
            self._update_stats(session, classification.assertion_type, classification.confidence)
            
            return job
    
    def _update_stats(self, session: Session, assertion_type: str, confidence: float):
        """
        Update classification statistics.
        
        Args:
            session: Database session
            assertion_type: Type of assertion
            confidence: Classification confidence
        """
        today = datetime.utcnow().date()
        
        # Get or create today's stats
        stmt = select(ClassificationStatsDB).where(
            ClassificationStatsDB.date >= datetime.combine(today, datetime.min.time())
        ).order_by(ClassificationStatsDB.date.desc())
        
        stats = session.execute(stmt).scalar_one_or_none()
        
        if stats is None:
            stats = ClassificationStatsDB(
                date=datetime.utcnow(),
                total_classifications=0,
                obligation_count=0,
                prohibition_count=0,
                permission_count=0,
                deadline_count=0,
                definition_count=0,
                avg_confidence=0.0
            )
            session.add(stats)
        
        # Update counts
        stats.total_classifications += 1
        
        if assertion_type == "obligation":
            stats.obligation_count += 1
        elif assertion_type == "prohibition":
            stats.prohibition_count += 1
        elif assertion_type == "permission":
            stats.permission_count += 1
        elif assertion_type == "deadline":
            stats.deadline_count += 1
        elif assertion_type == "definition":
            stats.definition_count += 1
        
        # Update average confidence
        old_avg = stats.avg_confidence
        old_count = stats.total_classifications - 1
        stats.avg_confidence = (old_avg * old_count + confidence) / stats.total_classifications
        
        session.commit()
    
    def get_classification(self, job_id: str) -> Optional[ClassificationJobDB]:
        """
        Get classification by job ID.
        
        Args:
            job_id: Job ID to retrieve
            
        Returns:
            ClassificationJobDB instance or None
        """
        with Session(self.engine) as session:
            stmt = select(ClassificationJobDB).where(ClassificationJobDB.job_id == job_id)
            return session.execute(stmt).scalar_one_or_none()
    
    def get_classifications_by_assertion(self, assertion_id: str) -> list[ClassificationJobDB]:
        """
        Get all classifications for an assertion.
        
        Args:
            assertion_id: Assertion ID
            
        Returns:
            List of ClassificationJobDB instances
        """
        with Session(self.engine) as session:
            stmt = select(ClassificationJobDB).where(
                ClassificationJobDB.assertion_id == assertion_id
            ).order_by(ClassificationJobDB.created_at.desc())
            return list(session.execute(stmt).scalars().all())
    
    def get_classifications_by_type(
        self,
        assertion_type: str,
        limit: int = 100
    ) -> list[ClassificationJobDB]:
        """
        Get classifications by type.
        
        Args:
            assertion_type: Type to filter by
            limit: Maximum number of results
            
        Returns:
            List of ClassificationJobDB instances
        """
        with Session(self.engine) as session:
            stmt = select(ClassificationJobDB).where(
                ClassificationJobDB.assertion_type == assertion_type
            ).order_by(ClassificationJobDB.created_at.desc()).limit(limit)
            return list(session.execute(stmt).scalars().all())
    
    def get_stats(self, days: int = 7) -> list[ClassificationStatsDB]:
        """
        Get classification statistics for the last N days.
        
        Args:
            days: Number of days to retrieve
            
        Returns:
            List of ClassificationStatsDB instances
        """
        with Session(self.engine) as session:
            cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            stmt = select(ClassificationStatsDB).where(
                ClassificationStatsDB.date >= cutoff
            ).order_by(ClassificationStatsDB.date.desc()).limit(days)
            return list(session.execute(stmt).scalars().all())
    
    def get_total_classifications(self) -> int:
        """
        Get total number of classifications.
        
        Returns:
            Total count
        """
        with Session(self.engine) as session:
            stmt = select(ClassificationJobDB)
            return len(list(session.execute(stmt).scalars().all()))
    
    def get_type_distribution(self) -> dict:
        """
        Get distribution of assertion types.
        
        Returns:
            Dictionary with type counts
        """
        with Session(self.engine) as session:
            stmt = select(ClassificationJobDB)
            jobs = session.execute(stmt).scalars().all()
            
            distribution = {
                "obligation": 0,
                "prohibition": 0,
                "permission": 0,
                "deadline": 0,
                "definition": 0
            }
            
            for job in jobs:
                if job.assertion_type in distribution:
                    distribution[job.assertion_type] += 1
            
            return distribution

# Made with Bob
