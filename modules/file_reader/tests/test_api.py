"""
Unit tests for File Reader API
"""
import os
import pytest
import tempfile
from fastapi.testclient import TestClient

from modules.file_reader.api import app
from modules.file_reader.database import db
from modules.file_reader.models import FileReaderJob


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def temp_txt_file():
    """Create a temporary TXT file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Test content for API testing")
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up database after each test"""
    yield
    # Clean up all jobs after test
    with db.get_session() as session:
        session.query(FileReaderJob).delete()
        session.commit()


class TestRootEndpoints:
    """Test root and health endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns module info"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "file-reader"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "port" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["module"] == "file-reader"


class TestReadEndpoint:
    """Test /api/read endpoint"""
    
    def test_read_file_success(self, client, temp_txt_file):
        """Test successful file reading"""
        response = client.post(
            "/api/read",
            json={
                "file_path": temp_txt_file,
                "file_type": "txt"
            }
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "file-reader"
        assert data["status"] == "success"
        assert "job_id" in data
        assert data["output"]["text"] == "Test content for API testing"
        assert data["output"]["char_count"] == 28
        assert data["output"]["encoding"] == "utf-8"
        assert "processing_time_ms" in data["metadata"]
    
    def test_read_file_auto_detect_type(self, client, temp_txt_file):
        """Test file reading with auto-detected type"""
        response = client.post(
            "/api/read",
            json={
                "file_path": temp_txt_file
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_read_nonexistent_file(self, client):
        """Test reading non-existent file returns 404"""
        response = client.post(
            "/api/read",
            json={
                "file_path": "/nonexistent/file.txt",
                "file_type": "txt"
            }
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_read_unsupported_file_type(self, client, temp_txt_file):
        """Test reading unsupported file type returns 400"""
        response = client.post(
            "/api/read",
            json={
                "file_path": temp_txt_file,
                "file_type": "xyz"
            }
        )
        
        assert response.status_code == 400
        assert "unsupported" in response.json()["detail"].lower()
    
    def test_read_file_creates_job_record(self, client, temp_txt_file):
        """Test that reading a file creates a job record in database"""
        response = client.post(
            "/api/read",
            json={
                "file_path": temp_txt_file,
                "file_type": "txt"
            }
        )
        
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        
        # Verify job exists in database
        with db.get_session() as session:
            job = session.query(FileReaderJob).filter_by(job_id=job_id).first()
            assert job is not None
            assert job.status == "success"
            assert job.file_path == temp_txt_file
            assert job.output_text == "Test content for API testing"


class TestJobEndpoints:
    """Test job management endpoints"""
    
    def test_get_job_by_id(self, client, temp_txt_file):
        """Test getting job details by ID"""
        # First create a job
        response = client.post(
            "/api/read",
            json={
                "file_path": temp_txt_file,
                "file_type": "txt"
            }
        )
        job_id = response.json()["job_id"]
        
        # Get job details
        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["job_id"] == job_id
        assert data["file_path"] == temp_txt_file
        assert data["status"] == "success"
        assert data["output_text"] == "Test content for API testing"
    
    def test_get_nonexistent_job(self, client):
        """Test getting non-existent job returns 404"""
        response = client.get("/api/jobs/nonexistent-job-id")
        assert response.status_code == 404
    
    def test_list_jobs(self, client, temp_txt_file):
        """Test listing all jobs"""
        # Create multiple jobs
        for i in range(3):
            client.post(
                "/api/read",
                json={
                    "file_path": temp_txt_file,
                    "file_type": "txt"
                }
            )
        
        # List jobs
        response = client.get("/api/jobs")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
    
    def test_list_jobs_with_pagination(self, client, temp_txt_file):
        """Test listing jobs with pagination"""
        # Create 5 jobs
        for i in range(5):
            client.post(
                "/api/read",
                json={
                    "file_path": temp_txt_file,
                    "file_type": "txt"
                }
            )
        
        # Get first 2 jobs
        response = client.get("/api/jobs?limit=2&offset=0")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Get next 2 jobs
        response = client.get("/api/jobs?limit=2&offset=2")
        assert response.status_code == 200
        assert len(response.json()) == 2
    
    def test_delete_job(self, client, temp_txt_file):
        """Test deleting a job"""
        # Create a job
        response = client.post(
            "/api/read",
            json={
                "file_path": temp_txt_file,
                "file_type": "txt"
            }
        )
        job_id = response.json()["job_id"]
        
        # Delete the job
        response = client.delete(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Verify job is deleted
        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 404
    
    def test_delete_nonexistent_job(self, client):
        """Test deleting non-existent job returns 404"""
        response = client.delete("/api/jobs/nonexistent-job-id")
        assert response.status_code == 404


class TestErrorHandling:
    """Test error handling in API"""
    
    def test_invalid_request_body(self, client):
        """Test invalid request body returns 422"""
        response = client.post(
            "/api/read",
            json={}
        )
        assert response.status_code == 422
    
    def test_error_job_is_recorded(self, client):
        """Test that failed jobs are recorded in database"""
        response = client.post(
            "/api/read",
            json={
                "file_path": "/nonexistent/file.txt",
                "file_type": "txt"
            }
        )
        
        assert response.status_code == 404
        
        # Check that error job exists in database
        with db.get_session() as session:
            jobs = session.query(FileReaderJob).filter_by(status="error").all()
            assert len(jobs) > 0
            assert jobs[0].error_message is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
