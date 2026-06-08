"""
Text Normalizer Service - Core business logic
Normalizes text by removing extra whitespace, fixing encoding, etc.
"""
import re
import time
from typing import Dict, Any, List


class TextNormalizerService:
    """
    Service for normalizing text
    """
    
    def __init__(self):
        """Initialize the text normalizer service"""
        pass
    
    def normalize(
        self,
        text: str,
        remove_extra_whitespace: bool = True,
        normalize_newlines: bool = True,
        fix_encoding: bool = True
    ) -> Dict[str, Any]:
        """
        Normalize text based on options
        
        Args:
            text: Input text to normalize
            remove_extra_whitespace: Remove extra spaces and tabs
            normalize_newlines: Normalize newlines to single \n
            fix_encoding: Fix common encoding issues
            
        Returns:
            Dictionary with normalized_text, changes_made, processing_time_ms,
            original_length, normalized_length
        """
        start_time = time.time()
        
        normalized_text = text
        changes_made = []
        
        # Fix encoding issues
        if fix_encoding:
            original = normalized_text
            normalized_text = self._fix_encoding(normalized_text)
            if normalized_text != original:
                changes_made.append("fixed_encoding")
        
        # Normalize newlines
        if normalize_newlines:
            original = normalized_text
            normalized_text = self._normalize_newlines(normalized_text)
            if normalized_text != original:
                changes_made.append("normalized_newlines")
        
        # Remove extra whitespace
        if remove_extra_whitespace:
            original = normalized_text
            normalized_text = self._remove_extra_whitespace(normalized_text)
            if normalized_text != original:
                changes_made.append("removed_extra_whitespace")
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "normalized_text": normalized_text,
            "changes_made": changes_made,
            "processing_time_ms": processing_time_ms,
            "original_length": len(text),
            "normalized_length": len(normalized_text)
        }
    
    def _fix_encoding(self, text: str) -> str:
        """
        Fix common encoding issues
        
        Args:
            text: Input text
            
        Returns:
            Text with fixed encoding
        """
        # Replace common encoding artifacts
        replacements = {
            '\ufeff': '',  # BOM
            '\u200b': '',  # Zero-width space
            '\u200c': '',  # Zero-width non-joiner
            '\u200d': '',  # Zero-width joiner
            '\xa0': ' ',   # Non-breaking space to regular space
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _normalize_newlines(self, text: str) -> str:
        """
        Normalize newlines to single \n
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized newlines
        """
        # Replace Windows CRLF with LF
        text = text.replace('\r\n', '\n')
        
        # Replace Mac CR with LF
        text = text.replace('\r', '\n')
        
        # Replace multiple consecutive newlines with maximum 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def _remove_extra_whitespace(self, text: str) -> str:
        """
        Remove extra whitespace (spaces, tabs)
        
        Args:
            text: Input text
            
        Returns:
            Text with extra whitespace removed
        """
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Replace multiple spaces with single space
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove spaces at start and end of lines
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        text = '\n'.join(lines)
        
        # Remove trailing/leading whitespace from entire text
        text = text.strip()
        
        return text


# Create singleton instance
_service = TextNormalizerService()


# Wrapper function for easy import
def normalize_text(
    text: str,
    remove_extra_whitespace: bool = True,
    normalize_newlines: bool = True,
    fix_encoding: bool = True
) -> Dict[str, Any]:
    """
    Wrapper function to normalize text using the singleton service.
    
    Args:
        text: Input text to normalize
        remove_extra_whitespace: Remove extra spaces and tabs
        normalize_newlines: Normalize newlines to single \n
        fix_encoding: Fix common encoding issues
        
    Returns:
        Dictionary with normalized_text and metadata
    """
    return _service.normalize(text, remove_extra_whitespace, normalize_newlines, fix_encoding)

# Made with Bob
