"""
Database layer for Condition Extractor module.
Uses unified database for better performance.
"""
import json
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

from shared.unified_database import unified_db
from shared.config_loader import config
from .models import (
    ConditionExtractionJob,
    ExtractedCondition,
    ConditionExtractionOutput
)


class Base(DeclarativeBase):
    """Base class for Condition Extractor models."""
    pass


class ConditionExtractionJobDB(Base):
    """Database model for condition extraction jobs."""
    __tablename__ = "condition_extraction_jobs"
    
    job_id: Mapped[str] = mapped_column(String, primary_key=True)
    assertion_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    assertion_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_conditions: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    total_conditions: Mapped[int] = mapped_column(Integer, nullable=False)
    total_exceptions: Mapped[int] = mapped_column(Integer, nullable=False)
    total_temporal: Mapped[int] = mapped_column(Integer, nullable=False)
    total_modal: Mapped[int] = mapped_column(Integer, nullable=False)
    average_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to conditions
    conditions: Mapped[List["ExtractedConditionDB"]] = relationship(
        "ExtractedConditionDB", 
        back_populates="job", 
        cascade="all, delete-orphan"
    )


class ExtractedConditionDB(Base):
    """Database model for extracted conditions."""
    __tablename__ = "extracted_conditions"
    
    condition_id: Mapped[str] = mapped_column(String, primary_key=True)
    job_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("condition_extraction_jobs.job_id"), 
        nullable=False, 
        index=True
    )
    condition_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_char: Mapped[int] = mapped_column(Integer, nullable=False)
    end_char: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    trigger_word: Mapped[str] = mapped_column(String, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationship to job
    job: Mapped["ConditionExtractionJobDB"] = relationship(
        "ConditionExtractionJobDB", 
        back_populates="conditions"
    )


class ConditionExtractorDatabase:
    """Database manager for condition extraction using unified database."""
    
    def __init__(self):
        """Initialize database connection with unified database."""
        # Initialize unified database with config
        unified_db_url = config.get_unified_database_url()
        unified_db.__init__(database_url=unified_db_url)
        
        # Register base class
        unified_db.register_base(Base)
        
        # Create tables
        unified_db.create_all_tables()
    
    @contextmanager
    def get_session(self):
        """Get database session from unified database."""
        with unified_db.get_session() as session:
            yield session
    
    def save_extraction_job(
        self,
        job_id: str,
        assertion_id: str,
        assertion_text: str,
        output: ConditionExtractionOutput
    ) -> ConditionExtractionJob:
        """
        Save condition extraction job to database.
        
        Args:
            job_id: Unique job identifier
            assertion_id: Assertion identifier
            assertion_text: Assertion text
            output: Extraction output
            
        Returns:
            Saved job model
        """
        with self.get_session() as session:
            # Create job record
            job_db = ConditionExtractionJobDB(
                job_id=job_id,
                assertion_id=assertion_id,
                assertion_text=assertion_text,
                output_conditions=json.dumps([c.dict() for c in output.conditions]),
                total_conditions=output.total_conditions,
                total_exceptions=output.total_exceptions,
                total_temporal=output.total_temporal,
                total_modal=output.total_modal,
                average_confidence=output.average_confidence,
                processing_time_ms=output.processing_time_ms,
                created_at=datetime.utcnow()
            )
            session.add(job_db)
            
            # Create condition records
            for condition in output.conditions:
                condition_db = ExtractedConditionDB(
                    condition_id=condition.condition_id,
                    job_id=job_id,
                    condition_type=condition.condition_type,
                    text=condition.text,
                    start_char=condition.start_char,
                    end_char=condition.end_char,
                    confidence=condition.confidence,
                    trigger_word=condition.trigger_word,
                    context=condition.context
                )
                session.add(condition_db)
            
            session.flush()
            
            # Convert to Pydantic model
            job = ConditionExtractionJob(
                job_id=job_db.job_id,
                assertion_id=job_db.assertion_id,
                assertion_text=job_db.assertion_text,
                output_conditions=job_db.output_conditions,
                total_conditions=job_db.total_conditions,
                total_exceptions=job_db.total_exceptions,
                total_temporal=job_db.total_temporal,
                total_modal=job_db.total_modal,
                average_confidence=job_db.average_confidence,
                processing_time_ms=job_db.processing_time_ms,
                created_at=job_db.created_at
            )
            
            return job
    
    def get_job(self, job_id: str) -> Optional[ConditionExtractionJob]:
        """
        Get extraction job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job model or None if not found
        """
        with self.get_session() as session:
            job_db = session.query(ConditionExtractionJobDB).filter_by(job_id=job_id).first()
            if not job_db:
                return None
            
            job = ConditionExtractionJob(
                job_id=job_db.job_id,
                assertion_id=job_db.assertion_id,
                assertion_text=job_db.assertion_text,
                output_conditions=job_db.output_conditions,
                total_conditions=job_db.total_conditions,
                total_exceptions=job_db.total_exceptions,
                total_temporal=job_db.total_temporal,
                total_modal=job_db.total_modal,
                average_confidence=job_db.average_confidence,
                processing_time_ms=job_db.processing_time_ms,
                created_at=job_db.created_at
            )
            
            return job
    
    def get_conditions_by_assertion(self, assertion_id: str) -> List[ExtractedCondition]:
        """
        Get all conditions for an assertion.
        
        Args:
            assertion_id: Assertion identifier
            
        Returns:
            List of extracted conditions
        """
        with self.get_session() as session:
            # Get all jobs for this assertion
            jobs = session.query(ConditionExtractionJobDB).filter_by(assertion_id=assertion_id).all()
            
            all_conditions = []
            for job in jobs:
                conditions_db = session.query(ExtractedConditionDB).filter_by(job_id=job.job_id).all()
                for cond_db in conditions_db:
                    condition = ExtractedCondition(
                        condition_id=cond_db.condition_id,
                        condition_type=cond_db.condition_type,
                        text=cond_db.text,
                        start_char=cond_db.start_char,
                        end_char=cond_db.end_char,
                        confidence=cond_db.confidence,
                        trigger_word=cond_db.trigger_word,
                        context=cond_db.context
                    )
                    all_conditions.append(condition)
            
            return all_conditions
    
    def get_all_jobs(self, limit: int = 100) -> List[ConditionExtractionJob]:
        """
        Get all extraction jobs.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of jobs
        """
        with self.get_session() as session:
            jobs_db = session.query(ConditionExtractionJobDB).order_by(
                ConditionExtractionJobDB.created_at.desc()
            ).limit(limit).all()
            
            jobs = []
            for job_db in jobs_db:
                job = ConditionExtractionJob(
                    job_id=job_db.job_id,
                    assertion_id=job_db.assertion_id,
                    assertion_text=job_db.assertion_text,
                    output_conditions=job_db.output_conditions,
                    total_conditions=job_db.total_conditions,
                    total_exceptions=job_db.total_exceptions,
                    total_temporal=job_db.total_temporal,
                    total_modal=job_db.total_modal,
                    average_confidence=job_db.average_confidence,
                    processing_time_ms=job_db.processing_time_ms,
                    created_at=job_db.created_at
                )
                jobs.append(job)
            
            return jobs


# Global database instance
db = ConditionExtractorDatabase()

# Made with Bob
