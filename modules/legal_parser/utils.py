"""Utility functions for Legal Parser module."""

from uuid import NAMESPACE_URL, uuid5


def generate_legal_unit_id(source_uri: str, path: str) -> str:
    """
    Generate deterministic UUID for legal unit.
    Same source_uri + path always produces same UUID.
    
    Args:
        source_uri: Source file path or URL
        path: Hierarchical path (e.g., "article:1/paragraph:1")
        
    Returns:
        UUID string
        
    Example:
        >>> generate_legal_unit_id("file:///doc.pdf", "article:1")
        '550e8400-e29b-41d4-a716-446655440000'
    """
    namespace_string = f"{source_uri}#{path}"
    return str(uuid5(NAMESPACE_URL, namespace_string))


def generate_akoma_eid(unit_type: str, number: str, parent_eid: str | None = None) -> str:
    """
    Generate Akoma Ntoso eId.
    
    Args:
        unit_type: Type of legal unit (article, paragraph, point, list, indent)
        number: Unit number (e.g., "1", "2", "1a")
        parent_eid: Parent eId (optional)
        
    Returns:
        Akoma Ntoso eId string
        
    Examples:
        >>> generate_akoma_eid("article", "1")
        'article_1'
        >>> generate_akoma_eid("paragraph", "1", "article_1")
        'article_1__para_1'
        >>> generate_akoma_eid("point", "1", "article_1__para_1")
        'article_1__para_1__point_1'
    """
    # Map unit types to Akoma Ntoso short names
    type_map = {
        "article": "article",
        "paragraph": "para",
        "point": "point",
        "list": "list",
        "indent": "indent"
    }
    
    short_type = type_map.get(unit_type, unit_type)
    
    if parent_eid:
        return f"{parent_eid}__{short_type}_{number}"
    return f"{short_type}_{number}"


def build_path(unit_type: str, number: str, parent_path: str | None = None) -> str:
    """
    Build hierarchical path for legal unit.
    
    Args:
        unit_type: Type of legal unit
        number: Unit number
        parent_path: Parent path (optional)
        
    Returns:
        Hierarchical path string
        
    Examples:
        >>> build_path("article", "1")
        'article:1'
        >>> build_path("paragraph", "1", "article:1")
        'article:1/paragraph:1'
        >>> build_path("point", "1", "article:1/paragraph:1")
        'article:1/paragraph:1/point:1'
    """
    segment = f"{unit_type}:{number}"
    
    if parent_path:
        return f"{parent_path}/{segment}"
    return segment


def extract_number_from_text(text: str) -> str | None:
    """
    Extract number from text (e.g., "Član 1." -> "1").
    
    Args:
        text: Text containing number
        
    Returns:
        Extracted number or None
        
    Examples:
        >>> extract_number_from_text("Član 1.")
        '1'
        >>> extract_number_from_text("(1) Text")
        '1'
        >>> extract_number_from_text("1) Text")
        '1'
    """
    import re
    
    # Try to find number in various formats
    patterns = [
        r'Član\s+(\d+[a-z]?)',  # Član 1, Član 1a
        r'\((\d+)\)',            # (1)
        r'(\d+)\)',              # 1)
        r'(\d+[a-z]?)\.?'        # 1, 1a, 1.
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def sanitize_text(text: str) -> str:
    """
    Sanitize text for storage (remove extra whitespace, normalize newlines).
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Normalize newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text.strip()


def calculate_ordinal(units: list, unit_type: str) -> int:
    """
    Calculate ordinal number for a unit type.
    
    Args:
        units: List of existing units
        unit_type: Type of unit to count
        
    Returns:
        Next ordinal number
        
    Example:
        >>> units = [{"unit_type": "article"}, {"unit_type": "article"}]
        >>> calculate_ordinal(units, "article")
        3
    """
    count = sum(1 for unit in units if unit.get("unit_type") == unit_type)
    return count + 1

# Made with Bob
