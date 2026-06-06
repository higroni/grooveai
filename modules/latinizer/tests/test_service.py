"""
Unit tests for Latinizer service.

Tests the core latinization logic and database persistence.
"""

import pytest
from modules.latinizer.service import service
from modules.latinizer.database import db as db_manager
from modules.latinizer.models import LatinizerJob


class TestLatinizerService:
    """Test cases for LatinizerService."""
    
    def test_latinize_cyrillic_text(self):
        """Test latinization of Cyrillic text."""
        cyrillic_text = "Закон о раду"
        result = service.latinize(cyrillic_text)
        
        assert result["latinized_text"] == "Zakon o radu"
        assert result["input_length"] == len(cyrillic_text)
        assert result["output_length"] == len("Zakon o radu")
        assert result["cyrillic_chars_converted"] == 10
        assert "processing_time_ms" in result
    
    def test_latinize_mixed_text(self):
        """Test latinization of mixed Cyrillic/Latin text."""
        mixed_text = "Члан 1: General provisions"
        result = service.latinize(mixed_text)
        
        assert "Član 1: General provisions" in result["latinized_text"]
        assert result["cyrillic_chars_converted"] == 4  # Only "Члан"
    
    def test_latinize_already_latin(self):
        """Test latinization of already Latin text."""
        latin_text = "Zakon o radu"
        result = service.latinize(latin_text)
        
        assert result["latinized_text"] == latin_text
        assert result["cyrillic_chars_converted"] == 0
    
    def test_latinize_empty_string(self):
        """Test latinization of empty string."""
        result = service.latinize("")
        
        assert result["latinized_text"] == ""
        assert result["input_length"] == 0
        assert result["output_length"] == 0
        assert result["cyrillic_chars_converted"] == 0
    
    def test_latinize_special_characters(self):
        """Test that special characters are preserved."""
        text = "Члан 1. (тачка 2)"
        result = service.latinize(text)
        
        assert "Član 1. (tačka 2)" in result["latinized_text"]
        # Parentheses and period should be preserved
        assert "(" in result["latinized_text"]
        assert ")" in result["latinized_text"]
        assert "." in result["latinized_text"]
    
    def test_is_cyrillic(self):
        """Test Cyrillic detection."""
        assert service.is_cyrillic("Закон") is True
        assert service.is_cyrillic("Zakon") is False
        assert service.is_cyrillic("Члан 1") is True
        assert service.is_cyrillic("Article 1") is False
    
    def test_get_cyrillic_count(self):
        """Test Cyrillic character counting."""
        assert service.get_cyrillic_count("Закон") == 5
        assert service.get_cyrillic_count("Zakon") == 0
        assert service.get_cyrillic_count("Члан 1: Article") == 4
    
    def test_uppercase_conversion(self):
        """Test uppercase Cyrillic conversion."""
        text = "ЗАКОН О РАДУ"
        result = service.latinize(text)
        
        assert result["latinized_text"] == "ZAKON O RADU"
    
    def test_lowercase_conversion(self):
        """Test lowercase Cyrillic conversion."""
        text = "закон о раду"
        result = service.latinize(text)
        
        assert result["latinized_text"] == "zakon o radu"
    
    def test_digraph_conversion(self):
        """Test digraph conversion (љ→lj, њ→nj, џ→dž)."""
        text = "љубав, њива, џеп"
        result = service.latinize(text)
        
        assert "ljubav" in result["latinized_text"]
        assert "njiva" in result["latinized_text"]
        assert "džep" in result["latinized_text"]


class TestLatinizerDatabase:
    """Test cases for database persistence."""
    
    def test_database_persistence(self):
        """Test that latinization results are correctly saved to database."""
        # Create a job
        input_text = "Закон о раду регулише права"
        output_text = "Zakon o radu regulise prava"
        
        job = LatinizerJob(
            input_text=input_text,
            output_text=output_text,
            cyrillic_chars_converted=22,
            processing_time_ms=1.5
        )
        
        # Save to database
        saved_job = db_manager.create(job)
        
        # Verify it was saved
        assert saved_job.id is not None
        assert saved_job.input_text == input_text
        assert saved_job.output_text == output_text
        assert saved_job.cyrillic_chars_converted == 22
        assert saved_job.processing_time_ms == 1.5
        assert saved_job.created_at is not None
        
        # Retrieve from database
        retrieved_job = db_manager.get_by_id(LatinizerJob, saved_job.id)
        assert retrieved_job is not None
        assert retrieved_job.input_text == input_text
        assert retrieved_job.output_text == output_text
        
        # Cleanup
        db_manager.delete(LatinizerJob, saved_job.id)
    
    def test_database_retrieval(self):
        """Test retrieving jobs from database."""
        # Create multiple jobs
        jobs_data = [
            ("Члан 1", "Clan 1", 4),
            ("Члан 2", "Clan 2", 4),
            ("Члан 3", "Clan 3", 4)
        ]
        
        created_ids = []
        for input_text, output_text, cyrillic_count in jobs_data:
            job = LatinizerJob(
                input_text=input_text,
                output_text=output_text,
                cyrillic_chars_converted=cyrillic_count,
                processing_time_ms=1.0
            )
            saved_job = db_manager.create(job)
            created_ids.append(saved_job.id)
        
        # Retrieve all jobs
        all_jobs = db_manager.get_all(LatinizerJob, limit=10)
        assert len(all_jobs) >= 3
        
        # Cleanup
        for job_id in created_ids:
            db_manager.delete(LatinizerJob, job_id)
    
    def test_database_deletion(self):
        """Test deleting jobs from database."""
        # Create a job
        job = LatinizerJob(
            input_text="Test",
            output_text="Test",
            cyrillic_chars_converted=0,
            processing_time_ms=1.0
        )
        saved_job = db_manager.create(job)
        job_id = saved_job.id
        
        # Delete it
        success = db_manager.delete(LatinizerJob, job_id)
        assert success is True
        
        # Verify it's gone
        retrieved_job = db_manager.get_by_id(LatinizerJob, job_id)
        assert retrieved_job is None
    
    def test_database_handles_large_text(self):
        """Test that database can handle large text."""
        # Create a large text (10KB)
        large_text = "Закон о раду " * 1000
        latinized_text = "Zakon o radu " * 1000
        
        job = LatinizerJob(
            input_text=large_text,
            output_text=latinized_text,
            cyrillic_chars_converted=10000,
            processing_time_ms=50.0
        )
        
        saved_job = db_manager.create(job)
        assert saved_job.id is not None
        
        # Retrieve and verify
        retrieved_job = db_manager.get_by_id(LatinizerJob, saved_job.id)
        assert retrieved_job is not None
        assert len(retrieved_job.input_text) == len(large_text)
        assert len(retrieved_job.output_text) == len(latinized_text)
        
        # Cleanup
        db_manager.delete(LatinizerJob, saved_job.id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
