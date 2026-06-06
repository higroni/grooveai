"""
Database models for Text Normalizer module
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TextNormalizerJob(Base):
    """
    Stores text normalization job information
    """
    __tablename__ = "text_normalizer_jobs"
    
    job_id = Column(String(36), primary_key=True)
    input_text = Column(Text, nullable=False)
    output_text = Column(Text, nullable=False)
    changes_made = Column(Text, nullable=True)  # JSON string of changes
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "input_text": self.input_text,
            "output_text": self.output_text,
            "changes_made": self.changes_made,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None
        }

# Made with Bob
