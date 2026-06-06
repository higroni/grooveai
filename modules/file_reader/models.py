"""
Database models for File Reader module
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FileReaderJob(Base):
    """
    Stores file reading job information
    """
    __tablename__ = "file_reader_jobs"
    
    job_id = Column(String(36), primary_key=True)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False)  # pending, processing, success, error
    output_text = Column(Text, nullable=True)
    char_count = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "status": self.status,
            "output_text": self.output_text,
            "char_count": self.char_count,
            "page_count": self.page_count,
            "processing_time_ms": self.processing_time_ms,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at is not None else None
        }

# Made with Bob
