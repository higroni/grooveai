"""
Unit tests for Vector Store database operations.
Tests the new hybrid embedding strategy with metadata support.
"""

import pytest
import json
import os
from datetime import datetime
from modules.vector_store.database import db
from modules.vector_store.models import EmbeddingJob, EmbeddingType


@pytest.fixture
def test_db():
    """Create a test database."""
    # Create a new test database manager with in-memory SQLite
    from modules.vector_store.database import EmbeddingDatabaseManager
    from modules.vector_store.models import Base
    
    test_db_manager = EmbeddingDatabaseManager()
    # Override with in-memory database
    test_db_manager.database_url = "sqlite:///:memory:"
    test_db_manager.engine = test_db_manager._create_engine("sqlite:///:memory:")
    test_db_manager.SessionLocal = test_db_manager._create_session_factory()
    test_db_manager.create_tables()
    
    yield test_db_manager
    
    # Cleanup
    test_db_manager.engine.dispose()
    
def _create_engine(self, url):
    """Helper to create engine for testing."""
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
    return create_engine(
        url,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

def _create_session_factory(self):
    """Helper to create session factory for testing."""
    from sqlalchemy.orm import sessionmaker
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=self.engine
    )


@pytest.fixture
def sample_embedding_job():
    """Create a sample embedding job."""
    return EmbeddingJob(
        job_id="emb_test_001",
        embedding_type=EmbeddingType.ASSERTION,
        input_text="Poslodavac je dužan da zaposlenom isplaćuje platu.",
        text_length=52,
        model_name="BAAI/bge-m3",
        embedding_dimension=1024,
        embeddings=json.dumps([0.1, 0.2, 0.3, 0.4, 0.5]),
        processing_time_ms=45.23,
        embedding_metadata=json.dumps({
            "assertion_type": "obligation",
            "confidence": 0.95,
            "entities": [{"type": "LEGAL_REF", "text": "Član 104"}],
            "conditions": []
        }),
        assertion_type="obligation",
        assertion_id="assert_001",
        source_document="zakon_o_radu.pdf",
        source_article="Član 104"
    )


def test_create_embedding_job(test_db, sample_embedding_job):
    """Test creating an embedding job."""
    # Create job
    created_job = test_db.create(sample_embedding_job)
    
    # Verify
    assert created_job.id is not None
    assert created_job.job_id == "emb_test_001"
    assert created_job.embedding_type == EmbeddingType.ASSERTION
    assert created_job.assertion_type == "obligation"
    assert created_job.source_article == "Član 104"


def test_get_by_job_id(test_db, sample_embedding_job):
    """Test retrieving job by job_id."""
    # Create job
    test_db.create(sample_embedding_job)
    
    # Retrieve
    retrieved_job = test_db.get_by_job_id("emb_test_001")
    
    # Verify
    assert retrieved_job is not None
    assert retrieved_job.job_id == "emb_test_001"
    assert retrieved_job.embedding_type == EmbeddingType.ASSERTION
    assert retrieved_job.input_text == sample_embedding_job.input_text


def test_get_by_job_id_not_found(test_db):
    """Test retrieving non-existent job."""
    retrieved_job = test_db.get_by_job_id("nonexistent")
    assert retrieved_job is None


def test_get_by_model(test_db):
    """Test retrieving jobs by model name."""
    # Create multiple jobs with different models
    job1 = EmbeddingJob(
        job_id="emb_001",
        embedding_type=EmbeddingType.ASSERTION,
        input_text="Test 1",
        text_length=6,
        model_name="BAAI/bge-m3",
        embedding_dimension=1024,
        embeddings=json.dumps([0.1, 0.2]),
        processing_time_ms=10.0
    )
    
    job2 = EmbeddingJob(
        job_id="emb_002",
        embedding_type=EmbeddingType.DOCUMENT,
        input_text="Test 2",
        text_length=6,
        model_name="BAAI/bge-m3",
        embedding_dimension=1024,
        embeddings=json.dumps([0.3, 0.4]),
        processing_time_ms=15.0
    )
    
    job3 = EmbeddingJob(
        job_id="emb_003",
        embedding_type=EmbeddingType.CHUNK,
        input_text="Test 3",
        text_length=6,
        model_name="other-model",
        embedding_dimension=512,
        embeddings=json.dumps([0.5, 0.6]),
        processing_time_ms=20.0
    )
    
    test_db.create(job1)
    test_db.create(job2)
    test_db.create(job3)
    
    # Retrieve jobs by model
    bge_jobs = test_db.get_by_model("BAAI/bge-m3")
    
    # Verify
    assert len(bge_jobs) == 2
    assert all(job.model_name == "BAAI/bge-m3" for job in bge_jobs)


def test_delete_by_job_id(test_db, sample_embedding_job):
    """Test deleting a job by job_id."""
    # Create job
    test_db.create(sample_embedding_job)
    
    # Verify it exists
    assert test_db.get_by_job_id("emb_test_001") is not None
    
    # Delete
    deleted = test_db.delete_by_job_id("emb_test_001")
    assert deleted is True
    
    # Verify it's gone
    assert test_db.get_by_job_id("emb_test_001") is None


def test_delete_nonexistent_job(test_db):
    """Test deleting a non-existent job."""
    deleted = test_db.delete_by_job_id("nonexistent")
    assert deleted is False


def test_get_all_with_pagination(test_db):
    """Test retrieving all jobs with pagination."""
    # Create multiple jobs
    for i in range(5):
        job = EmbeddingJob(
            job_id=f"emb_{i:03d}",
            embedding_type=EmbeddingType.ASSERTION,
            input_text=f"Test {i}",
            text_length=6,
            model_name="BAAI/bge-m3",
            embedding_dimension=1024,
            embeddings=json.dumps([0.1 * i, 0.2 * i]),
            processing_time_ms=10.0 * i
        )
        test_db.create(job)
    
    # Test pagination
    page1 = test_db.get_all(EmbeddingJob, limit=2, offset=0)
    page2 = test_db.get_all(EmbeddingJob, limit=2, offset=2)
    
    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].job_id != page2[0].job_id


def test_count(test_db):
    """Test counting jobs."""
    # Initially empty
    assert test_db.count(EmbeddingJob) == 0
    
    # Create jobs
    for i in range(3):
        job = EmbeddingJob(
            job_id=f"emb_{i:03d}",
            embedding_type=EmbeddingType.ASSERTION,
            input_text=f"Test {i}",
            text_length=6,
            model_name="BAAI/bge-m3",
            embedding_dimension=1024,
            embeddings=json.dumps([0.1, 0.2]),
            processing_time_ms=10.0
        )
        test_db.create(job)
    
    # Verify count
    assert test_db.count(EmbeddingJob) == 3


def test_embedding_types(test_db):
    """Test different embedding types."""
    # Create jobs with different types
    types = [EmbeddingType.ASSERTION, EmbeddingType.DOCUMENT, EmbeddingType.CHUNK]
    
    for i, emb_type in enumerate(types):
        job = EmbeddingJob(
            job_id=f"emb_{emb_type.value}_{i}",
            embedding_type=emb_type,
            input_text=f"Test {emb_type.value}",
            text_length=10,
            model_name="BAAI/bge-m3",
            embedding_dimension=1024,
            embeddings=json.dumps([0.1, 0.2]),
            processing_time_ms=10.0
        )
        test_db.create(job)
    
    # Verify all types were created
    all_jobs = test_db.get_all(EmbeddingJob)
    assert len(all_jobs) == 3
    
    created_types = {job.embedding_type for job in all_jobs}
    assert created_types == {EmbeddingType.ASSERTION, EmbeddingType.DOCUMENT, EmbeddingType.CHUNK}


def test_metadata_storage(test_db):
    """Test storing and retrieving metadata."""
    metadata = {
        "assertion_type": "obligation",
        "confidence": 0.95,
        "entities": [
            {"type": "LEGAL_REF", "text": "Član 104", "start": 0, "end": 8}
        ],
        "conditions": [
            {"type": "condition", "text": "ako je zaposlen", "start": 10, "end": 25}
        ],
        "entity_count": 1,
        "condition_count": 1
    }
    
    job = EmbeddingJob(
        job_id="emb_metadata_test",
        embedding_type=EmbeddingType.ASSERTION,
        input_text="Test with metadata",
        text_length=18,
        model_name="BAAI/bge-m3",
        embedding_dimension=1024,
        embeddings=json.dumps([0.1, 0.2]),
        processing_time_ms=10.0,
        embedding_metadata=json.dumps(metadata),
        assertion_type="obligation",
        assertion_id="assert_001"
    )
    
    test_db.create(job)
    
    # Retrieve and verify
    retrieved = test_db.get_by_job_id("emb_metadata_test")
    assert retrieved is not None
    
    retrieved_metadata = json.loads(retrieved.embedding_metadata)
    assert retrieved_metadata["assertion_type"] == "obligation"
    assert retrieved_metadata["confidence"] == 0.95
    assert len(retrieved_metadata["entities"]) == 1
    assert len(retrieved_metadata["conditions"]) == 1


def test_assertion_filtering_fields(test_db):
    """Test quick filtering fields for assertions."""
    # Create jobs with different assertion types
    assertion_types = ["obligation", "prohibition", "permission", "deadline", "definition"]
    
    for i, a_type in enumerate(assertion_types):
        job = EmbeddingJob(
            job_id=f"emb_{a_type}_{i}",
            embedding_type=EmbeddingType.ASSERTION,
            input_text=f"Test {a_type}",
            text_length=10,
            model_name="BAAI/bge-m3",
            embedding_dimension=1024,
            embeddings=json.dumps([0.1, 0.2]),
            processing_time_ms=10.0,
            assertion_type=a_type,
            assertion_id=f"assert_{i:03d}",
            source_document="zakon_o_radu.pdf",
            source_article=f"Član {i+1}"
        )
        test_db.create(job)
    
    # Verify all were created
    all_jobs = test_db.get_all(EmbeddingJob)
    assert len(all_jobs) == 5
    
    # Verify filtering fields
    created_types = {job.assertion_type for job in all_jobs}
    assert created_types == set(assertion_types)


def test_large_embedding_storage(test_db):
    """Test storing large embeddings (1024 dimensions)."""
    # Create a realistic 1024-dimensional embedding
    large_embedding = [0.001 * i for i in range(1024)]
    
    job = EmbeddingJob(
        job_id="emb_large",
        embedding_type=EmbeddingType.ASSERTION,
        input_text="Test with large embedding",
        text_length=25,
        model_name="BAAI/bge-m3",
        embedding_dimension=1024,
        embeddings=json.dumps(large_embedding),
        processing_time_ms=45.0
    )
    
    test_db.create(job)
    
    # Retrieve and verify
    retrieved = test_db.get_by_job_id("emb_large")
    assert retrieved is not None
    
    retrieved_embedding = json.loads(retrieved.embeddings)
    assert len(retrieved_embedding) == 1024
    assert retrieved_embedding[0] == 0.0
    assert abs(retrieved_embedding[1023] - 1.023) < 0.001


def test_timestamp_creation(test_db, sample_embedding_job):
    """Test that created_at timestamp is set automatically."""
    # Create job
    created_job = test_db.create(sample_embedding_job)
    
    # Verify timestamp
    assert created_job.created_at is not None
    assert isinstance(created_job.created_at, datetime)
    
    # Verify it's recent (within last minute)
    time_diff = datetime.utcnow() - created_job.created_at
    assert time_diff.total_seconds() < 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
