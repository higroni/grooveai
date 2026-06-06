"""Tests for Legal Parser database operations."""

import pytest
from modules.legal_parser.database import LegalParserDatabaseManager
from modules.legal_parser.models import LegalParserJob


class TestLegalParserDatabase:
    """Test database operations."""
    
    def test_create_and_retrieve_job(self, db: LegalParserDatabaseManager):
        """Test creating and retrieving a job."""
        # Create job
        job = LegalParserJob(
            input_text="Član 1.\nTest",
            source_uri="file:///test.pdf",
            filename="test.pdf",
            canonical_json='{"document": {}}',
            total_units=1,
            total_articles=1,
            total_paragraphs=0,
            total_points=0,
            document_title="Test Document",
            document_type="zakon",
            language_code="sr-Latn",
            processing_time_ms=10.5
        )
        
        # Create
        saved_job = db.create(job)
        assert saved_job.id is not None
        
        # Retrieve
        retrieved = db.get_by_id(LegalParserJob, saved_job.id)
        assert retrieved is not None
        assert retrieved.filename == "test.pdf"
        assert retrieved.total_articles == 1
        assert retrieved.document_title == "Test Document"
    
    def test_get_all_jobs(self, db: LegalParserDatabaseManager):
        """Test retrieving all jobs."""
        # Create multiple jobs
        for i in range(3):
            job = LegalParserJob(
                input_text=f"Član {i+1}.\nTest",
                source_uri=f"file:///test{i}.pdf",
                filename=f"test{i}.pdf",
                canonical_json='{"document": {}}',
                total_units=1,
                total_articles=1,
                total_paragraphs=0,
                total_points=0,
                document_title=f"Test Document {i}",
                document_type="zakon",
                language_code="sr-Latn",
                processing_time_ms=10.5
            )
            db.create(job)
        
        # Retrieve all
        jobs = db.get_all(LegalParserJob)
        assert len(jobs) >= 3
    
    def test_delete_job(self, db: LegalParserDatabaseManager):
        """Test deleting a job."""
        # Create job
        job = LegalParserJob(
            input_text="Član 1.\nTest",
            source_uri="file:///test.pdf",
            filename="test.pdf",
            canonical_json='{"document": {}}',
            total_units=1,
            total_articles=1,
            total_paragraphs=0,
            total_points=0,
            document_title="Test Document",
            document_type="zakon",
            language_code="sr-Latn",
            processing_time_ms=10.5
        )
        
        # Create
        saved_job = db.create(job)
        job_id = saved_job.id
        
        # Delete
        result = db.delete(LegalParserJob, job_id)
        assert result is True
        
        # Verify deleted
        retrieved = db.get_by_id(LegalParserJob, job_id)
        assert retrieved is None
    
    def test_count_jobs(self, db: LegalParserDatabaseManager):
        """Test counting jobs."""
        # Get initial count
        initial_count = len(db.get_all(LegalParserJob))
        
        # Create jobs
        for i in range(2):
            job = LegalParserJob(
                input_text=f"Član {i+1}.\nTest",
                source_uri=f"file:///test{i}.pdf",
                filename=f"test{i}.pdf",
                canonical_json='{"document": {}}',
                total_units=5,
                total_articles=2,
                total_paragraphs=2,
                total_points=1,
                document_title=f"Test Document {i}",
                document_type="zakon",
                language_code="sr-Latn",
                processing_time_ms=10.5
            )
            db.create(job)
        
        # Verify count increased
        final_count = len(db.get_all(LegalParserJob))
        assert final_count == initial_count + 2

# Made with Bob
