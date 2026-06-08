"""
Script to add wrapper functions to all service modules.
This enables direct function imports for batch processing.
"""

# Text Normalizer wrapper
text_normalizer_wrapper = '''

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
        normalize_newlines: Normalize newlines to single \\n
        fix_encoding: Fix common encoding issues
        
    Returns:
        Dictionary with normalized_text and metadata
    """
    return _service.normalize(text, remove_extra_whitespace, normalize_newlines, fix_encoding)
'''

# Legal Parser wrapper
legal_parser_wrapper = '''

# Create singleton instance
_service = LegalParserService()


# Wrapper function for easy import
def parse_legal_document(
    text: str,
    document_id: str,
    db_session=None
) -> Dict[str, Any]:
    """
    Wrapper function to parse legal document using the singleton service.
    
    Args:
        text: Document text
        document_id: Document identifier
        db_session: Optional database session
        
    Returns:
        Dictionary with parsed structure
    """
    result = _service.parse_document(
        text=text,
        source_uri=f"doc://{document_id}",
        filename=document_id,
        document_type="law",
        language_code="sr"
    )
    
    # Convert to dict format expected by batch processor
    return {
        'units': [unit.dict() for unit in result.units],
        'statistics': result.statistics.dict() if result.statistics else None
    }
'''

# Assertion Extractor wrapper
assertion_extractor_wrapper = '''

# Create singleton instance
_service = AssertionExtractorService()


# Wrapper function for easy import
def extract_assertions(content: str, min_confidence: float = 0.5) -> Dict[str, Any]:
    """
    Wrapper function to extract assertions using the singleton service.
    
    Args:
        content: Legal unit content text
        min_confidence: Minimum confidence threshold (0-1)
        
    Returns:
        Dictionary with assertions and statistics
    """
    result = _service.extract_assertions(content, min_confidence)
    return {
        'assertions': [a.dict() for a in result.assertions],
        'statistics': result.statistics.dict() if result.statistics else None
    }
'''

# Condition Extractor wrapper
condition_extractor_wrapper = '''

# Create singleton instance
_service = ConditionExtractorService()


# Wrapper function for easy import
def extract_conditions(assertions: List[Dict[str, Any]], language: str = "sr") -> Dict[str, Any]:
    """
    Wrapper function to extract conditions using the singleton service.
    
    Args:
        assertions: List of assertion dictionaries
        language: Language code (sr or en)
        
    Returns:
        Dictionary with conditions and statistics
    """
    # Convert dict assertions to Assertion objects
    assertion_objs = [Assertion(**a) for a in assertions]
    
    result = _service.extract_conditions(assertion_objs, language)
    return {
        'conditions': [c.dict() for c in result.conditions],
        'statistics': result.statistics.dict() if result.statistics else None
    }
'''

# Assertion Classifier wrapper
assertion_classifier_wrapper = '''

# Create singleton instance
_service = AssertionClassifierService()


# Wrapper function for easy import
def classify_assertions(assertions: List[Dict[str, Any]], language: str = "sr") -> Dict[str, Any]:
    """
    Wrapper function to classify assertions using the singleton service.
    
    Args:
        assertions: List of assertion dictionaries
        language: Language code (sr or en)
        
    Returns:
        Dictionary with classified assertions
    """
    # Convert dict assertions to Assertion objects
    assertion_objs = [Assertion(**a) for a in assertions]
    
    result = _service.classify_assertions(assertion_objs, language)
    return {
        'classified_assertions': [c.dict() for c in result.classified_assertions],
        'statistics': result.statistics.dict() if result.statistics else None
    }
'''

print("Wrapper functions defined.")
print("\nTo add these manually:")
print("1. text_normalizer/service.py - add before '# Made with Bob'")
print("2. legal_parser/service.py - add before '# Made with Bob'")
print("3. assertion_extractor/service.py - add before '# Made with Bob'")
print("4. condition_extractor/service.py - add before '# Made with Bob'")
print("5. assertion_classifier/service.py - add before '# Made with Bob'")