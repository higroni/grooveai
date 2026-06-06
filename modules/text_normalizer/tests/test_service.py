"""
Unit tests for Text Normalizer Service
"""
import pytest
from modules.text_normalizer.service import TextNormalizerService


class TestTextNormalizerService:
    """Test cases for TextNormalizerService"""
    
    @pytest.fixture
    def service(self):
        """Create a TextNormalizerService instance"""
        return TextNormalizerService()
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None
    
    def test_remove_extra_whitespace(self, service):
        """Test removing extra whitespace"""
        text = "Zakon   o  radu"
        result = service.normalize(text, remove_extra_whitespace=True, normalize_newlines=False, fix_encoding=False)
        
        assert result["normalized_text"] == "Zakon o radu"
        assert "removed_extra_whitespace" in result["changes_made"]
    
    def test_normalize_newlines(self, service):
        """Test normalizing newlines"""
        text = "Line 1\r\nLine 2\rLine 3\n\n\nLine 4"
        result = service.normalize(text, remove_extra_whitespace=False, normalize_newlines=True, fix_encoding=False)
        
        assert "\r\n" not in result["normalized_text"]
        assert "\r" not in result["normalized_text"]
        assert "normalized_newlines" in result["changes_made"]
    
    def test_fix_encoding(self, service):
        """Test fixing encoding issues"""
        text = "\ufeffTest\xa0text"
        result = service.normalize(text, remove_extra_whitespace=False, normalize_newlines=False, fix_encoding=True)
        
        assert "\ufeff" not in result["normalized_text"]
        assert "\xa0" not in result["normalized_text"]
        assert "fixed_encoding" in result["changes_made"]
    
    def test_combined_normalization(self, service):
        """Test all normalizations combined"""
        text = "\ufeffZakon   o  radu\r\n\r\nČlan 1"
        result = service.normalize(text)
        
        assert result["normalized_text"] == "Zakon o radu\n\nČlan 1"
        assert len(result["changes_made"]) > 0
    
    def test_no_changes_needed(self, service):
        """Test when no changes are needed"""
        text = "Clean text"
        result = service.normalize(text)
        
        assert result["normalized_text"] == "Clean text"
        assert len(result["changes_made"]) == 0
    
    def test_processing_time_recorded(self, service):
        """Test that processing time is recorded"""
        text = "Test text"
        result = service.normalize(text)
        
        assert "processing_time_ms" in result
        assert isinstance(result["processing_time_ms"], int)
        assert result["processing_time_ms"] >= 0
    
    def test_length_tracking(self, service):
        """Test original and normalized length tracking"""
        text = "Test   text"
        result = service.normalize(text)
        
        assert result["original_length"] == len(text)
        assert result["normalized_length"] == len(result["normalized_text"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
