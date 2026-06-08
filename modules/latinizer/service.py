"""
Latinizer Service.

This module converts Serbian Cyrillic text to Latin script.
Uses standard Serbian Cyrillic-to-Latin transliteration rules.
"""

import sys
import time
from typing import Dict, Any
from shared.config_loader import config
from shared.logger import get_module_logger

# Set UTF-8 encoding for stdout to handle Latin characters with diacritics
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

# Initialize logger
logger = get_module_logger("latinizer", config.get_log_level())


class LatinizerService:
    """
    Service for converting Cyrillic to Latin text.
    
    Implements standard Serbian Cyrillic-to-Latin transliteration.
    """
    
    # Serbian Cyrillic to Latin mapping
    CYRILLIC_TO_LATIN = {
        # Lowercase
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'ђ': 'đ', 'е': 'e', 'ж': 'ž', 'з': 'z', 'и': 'i',
        'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj', 'м': 'm',
        'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'ћ': 'ć', 'у': 'u', 'ф': 'f',
        'х': 'h', 'ц': 'c', 'ч': 'č', 'џ': 'dž', 'ш': 'š',
        
        # Uppercase
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Ђ': 'Đ', 'Е': 'E', 'Ж': 'Ž', 'З': 'Z', 'И': 'I',
        'Ј': 'J', 'К': 'K', 'Л': 'L', 'Љ': 'Lj', 'М': 'M',
        'Н': 'N', 'Њ': 'Nj', 'О': 'O', 'П': 'P', 'Р': 'R',
        'С': 'S', 'Т': 'T', 'Ћ': 'Ć', 'У': 'U', 'Ф': 'F',
        'Х': 'H', 'Ц': 'C', 'Ч': 'Č', 'Џ': 'Dž', 'Ш': 'Š',
    }
    
    def __init__(self):
        """Initialize the latinizer service."""
        logger.debug("Latinizer service initialized")
    
    def latinize(self, text: str) -> Dict[str, Any]:
        """
        Convert Cyrillic text to Latin.
        
        Args:
            text: Input text (may contain Cyrillic)
        
        Returns:
            Dictionary containing:
            - latinized_text: Converted text
            - input_length: Length of input text
            - output_length: Length of output text
            - cyrillic_chars_converted: Number of Cyrillic characters converted
            - processing_time_ms: Processing time in milliseconds
        """
        start_time = time.time()
        
        try:
            # Convert text
            latinized_text = ""
            cyrillic_count = 0
            
            for char in text:
                if char in self.CYRILLIC_TO_LATIN:
                    latinized_text += self.CYRILLIC_TO_LATIN[char]
                    cyrillic_count += 1
                else:
                    latinized_text += char
            
            processing_time = (time.time() - start_time) * 1000
            
            result = {
                "latinized_text": latinized_text,
                "input_length": len(text),
                "output_length": len(latinized_text),
                "cyrillic_chars_converted": cyrillic_count,
                "processing_time_ms": round(processing_time, 2)
            }
            
            logger.debug(
                f"Latinized {len(text)} chars, converted {cyrillic_count} Cyrillic chars "
                f"in {processing_time:.2f}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error latinizing text: {e}", exc_info=True)
            raise
    
    def is_cyrillic(self, text: str) -> bool:
        """
        Check if text contains Cyrillic characters.
        
        Args:
            text: Text to check
        
        Returns:
            True if text contains at least one Cyrillic character
        """
        return any(char in self.CYRILLIC_TO_LATIN for char in text)
    
    def get_cyrillic_count(self, text: str) -> int:
        """
        Count Cyrillic characters in text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Number of Cyrillic characters
        """
        return sum(1 for char in text if char in self.CYRILLIC_TO_LATIN)


# Create singleton instance
service = LatinizerService()

# Wrapper function for easy import
def latinize_text(text: str) -> Dict[str, Any]:
    """
    Wrapper function to latinize text using the singleton service.
    
    Args:
        text: Input text (may contain Cyrillic)
        
    Returns:
        Dictionary with latinized_text and metadata
    """
    return service.latinize(text)


# Example usage
if __name__ == "__main__":
    print("Testing Latinizer Service...")
    
    # Test 1: Cyrillic text
    test_text = "Закон о раду регулише права и обавезе запослених."
    print("\nTest 1: Cyrillic text")
    
    result = service.latinize(test_text)
    print(f"Input length: {result['input_length']}")
    print(f"Latinized: {result['latinized_text']}")
    print(f"Cyrillic chars converted: {result['cyrillic_chars_converted']}")
    print(f"Processing time: {result['processing_time_ms']}ms")
    
    # Test 2: Mixed text
    test_text2 = "Члан 1: General provisions"
    print("\nTest 2: Mixed Cyrillic/Latin text")
    
    result2 = service.latinize(test_text2)
    print(f"Latinized: {result2['latinized_text']}")
    print(f"Cyrillic chars converted: {result2['cyrillic_chars_converted']}")
    
    # Test 3: Already Latin
    test_text3 = "Zakon o radu"
    print("\nTest 3: Already Latin text")
    
    result3 = service.latinize(test_text3)
    print(f"Latinized: {result3['latinized_text']}")
    print(f"Cyrillic chars converted: {result3['cyrillic_chars_converted']}")
    
    print("\nLatinizer service testing complete!")

# Made with Bob
