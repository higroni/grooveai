"""SQLAlchemy models for Legal Parser module."""

from datetime import datetime
from sqlalchemy import Integer, Text, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class LegalParserJob(Base):
    """
    Legal Parser job model.
    Stores parsed legal documents in Akoma Ntoso-compatible JSON format.
    """
    __tablename__ = "legal_parser_jobs"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Input data
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_uri: Mapped[str] = mapped_column(Text, nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Output data (Akoma Ntoso-compatible JSON)
    canonical_json: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Statistics
    total_units: Mapped[int] = mapped_column(Integer, nullable=False)
    total_articles: Mapped[int] = mapped_column(Integer, nullable=False)
    total_paragraphs: Mapped[int] = mapped_column(Integer, nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Document metadata
    document_title: Mapped[str] = mapped_column(Text, nullable=True)
    document_type: Mapped[str] = mapped_column(Text, nullable=False, default="law")
    language_code: Mapped[str] = mapped_column(Text, nullable=False, default="sr")
    
    # Processing metadata
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<LegalParserJob(id={self.id}, filename='{self.filename}', "
            f"total_units={self.total_units}, total_articles={self.total_articles})>"
        )

# Made with Bob
