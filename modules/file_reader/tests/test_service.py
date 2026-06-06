"""
Unit tests for File Reader Service
"""
import os
import pytest
import tempfile
from pathlib import Path

from modules.file_reader.service import FileReaderService


class TestFileReaderService:
    """Test cases for FileReaderService"""
    
    @pytest.fixture
    def service(self):
        """Create a FileReaderService instance"""
        return FileReaderService()
    
    @pytest.fixture
    def temp_txt_file(self):
        """Create a temporary TXT file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Test content\nLine 2\nLine 3")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)
    
    @pytest.fixture
    def temp_txt_file_cyrillic(self):
        """Create a temporary TXT file with Cyrillic content"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Тестни садржај\nЛинија 2\nЛинија 3")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None
        assert service.SUPPORTED_FORMATS == ["pdf", "docx", "txt"]
    
    def test_read_txt_file(self, service, temp_txt_file):
        """Test reading a TXT file"""
        result = service.read_file(temp_txt_file, "txt")
        
        assert result is not None
        assert "text" in result
        assert "encoding" in result
        assert "char_count" in result
        assert "page_count" in result
        assert "processing_time_ms" in result
        
        assert result["text"] == "Test content\nLine 2\nLine 3"
        assert result["char_count"] == 28
        assert result["page_count"] >= 1
        assert result["processing_time_ms"] >= 0
    
    def test_read_txt_file_cyrillic(self, service, temp_txt_file_cyrillic):
        """Test reading a TXT file with Cyrillic content"""
        result = service.read_file(temp_txt_file_cyrillic, "txt")
        
        assert result is not None
        assert "Тестни садржај" in result["text"]
        assert "Линија 2" in result["text"]
        assert result["char_count"] > 0
    
    def test_read_file_auto_detect_type(self, service, temp_txt_file):
        """Test automatic file type detection"""
        result = service.read_file(temp_txt_file)
        
        assert result is not None
        assert result["text"] == "Test content\nLine 2\nLine 3"
    
    def test_read_nonexistent_file(self, service):
        """Test reading a non-existent file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            service.read_file("/nonexistent/file.txt", "txt")
    
    def test_read_unsupported_file_type(self, service, temp_txt_file):
        """Test reading unsupported file type raises ValueError"""
        with pytest.raises(ValueError, match="Unsupported file type"):
            service.read_file(temp_txt_file, "xyz")
    
    def test_read_txt_with_different_encodings(self, service):
        """Test reading TXT files with different encodings"""
        # Create file with UTF-8 BOM
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8-sig') as f:
            f.write("Test with BOM")
            temp_path = f.name
        
        try:
            result = service.read_file(temp_path, "txt")
            assert "Test with BOM" in result["text"]
        finally:
            os.unlink(temp_path)
    
    def test_processing_time_is_recorded(self, service, temp_txt_file):
        """Test that processing time is recorded"""
        result = service.read_file(temp_txt_file, "txt")
        
        assert "processing_time_ms" in result
        assert isinstance(result["processing_time_ms"], int)
        assert result["processing_time_ms"] >= 0
    
    def test_page_count_estimation(self, service):
        """Test page count estimation for TXT files"""
        # Create a large text file (more than 3000 chars)
        large_text = "A" * 6000
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(large_text)
            temp_path = f.name
        
        try:
            result = service.read_file(temp_path, "txt")
            assert result["page_count"] >= 2  # Should estimate at least 2 pages
        finally:
            os.unlink(temp_path)
    
    def test_empty_file(self, service):
        """Test reading an empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            temp_path = f.name
        
        try:
            result = service.read_file(temp_path, "txt")
            assert result["text"] == ""
            assert result["char_count"] == 0
            assert result["page_count"] >= 1
        finally:
            os.unlink(temp_path)
    
    def test_file_with_special_characters(self, service):
        """Test reading file with special characters"""
        special_text = "Test with special chars: @#$%^&*()_+-=[]{}|;:',.<>?/~`"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(special_text)
            temp_path = f.name
        
        try:
            result = service.read_file(temp_path, "txt")
            assert result["text"] == special_text
        finally:
            os.unlink(temp_path)
    
    def test_multiline_file(self, service):
        """Test reading file with multiple lines"""
        lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
        text = "\n".join(lines)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            temp_path = f.name
        
        try:
            result = service.read_file(temp_path, "txt")
            assert result["text"] == text
            assert result["char_count"] == len(text)
        finally:
            os.unlink(temp_path)


class TestFileReaderServicePDF:
    """Test cases for PDF reading (requires sample PDF)"""
    
    @pytest.fixture
    def service(self):
        """Create a FileReaderService instance"""
        return FileReaderService()
    
    def test_read_sample_pdf(self, service):
        """Test reading the sample PDF file if it exists"""
        from shared.config_loader import config
        sample_file = config.get_sample_file()
        
        if not os.path.exists(sample_file):
            pytest.skip(f"Sample PDF not found: {sample_file}")
        
        result = service.read_file(sample_file, "pdf")
        
        assert result is not None
        assert "text" in result
        assert len(result["text"]) > 0
        assert result["char_count"] > 0
        assert result["page_count"] > 0
        assert result["encoding"] == "utf-8"
        assert result["processing_time_ms"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
