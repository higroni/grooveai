"""Regex patterns for parsing Serbian legal documents."""

import re
from typing import Pattern


class LegalPatterns:
    """
    Regex patterns for Serbian legal document structure.
    Supports both Cyrillic and Latin scripts.
    """
    
    # Article patterns - support both "Član" (with diacritics) and "Clan" (without)
    # IMPORTANT: Only matches capitalized "Član" or "Clan" at start of line (not "član" or "clan")
    # This prevents false positives from references like "član 179. stav 3." in middle of sentences
    ARTICLE_SIMPLE: Pattern = re.compile(
        r'^[ČC]lan\s+(\d+[a-z]?)\.?\s*$'
    )
    
    ARTICLE_WITH_HEADING: Pattern = re.compile(
        r'^[ČC]lan\s+(\d+[a-z]?)\.?\s+(.+)$'
    )
    
    # Paragraph patterns (Stav)
    PARAGRAPH: Pattern = re.compile(
        r'^\((\d+)\)\s+(.+)$'
    )
    
    # Point patterns (Tačka)
    POINT: Pattern = re.compile(
        r'^(\d+)\)\s+(.+)$'
    )
    
    # Subpoint patterns (Podtačka) - within a point
    SUBPOINT: Pattern = re.compile(
        r'^\((\d+)\)\s+(.+)$'
    )
    
    # Indent patterns (Alineja)
    INDENT: Pattern = re.compile(
        r'^[-–—]\s+(.+)$'
    )
    
    # Document title patterns
    TITLE_ZAKON: Pattern = re.compile(
        r'^ZAKON\s*$',
        re.IGNORECASE
    )
    
    TITLE_O: Pattern = re.compile(
        r'^o\s+(.+)$',
        re.IGNORECASE
    )
    
    # Official gazette pattern
    OFFICIAL_GAZETTE: Pattern = re.compile(
        r'["\"]Službeni\s+glasnik\s+RS["\"]?\s+br\.?\s*(\d+(?:/\d+)?)',
        re.IGNORECASE
    )
    
    # Date pattern (Serbian format)
    DATE_PATTERN: Pattern = re.compile(
        r'(\d{1,2})\.?\s+(januar|februar|mart|april|maj|jun|jul|avgust|septembar|oktobar|novembar|decembar)[a-z]*\s+(\d{4})',
        re.IGNORECASE
    )
    
    # Section title pattern (e.g., "1. Predmet", "2. Značenje pojedinih pojmova")
    SECTION_TITLE: Pattern = re.compile(
        r'^\d+\.\s+(.+)$'
    )
    
    # Metadata line pattern (references to opinions, models, case law)
    # Supports both "Mišljenja" (with diacritics) and "Misljenja" (without)
    METADATA_LINE: Pattern = re.compile(
        r'^Mi[sš]ljenja.*praksa$',
        re.IGNORECASE
    )
    
    @staticmethod
    def is_article(line: str) -> tuple[bool, str | None, str | None]:
        """
        Check if line is an article.
        
        Returns:
            tuple: (is_article, number, heading)
        """
        line = line.strip()
        
        # Try article with heading
        match = LegalPatterns.ARTICLE_WITH_HEADING.match(line)
        if match:
            return True, match.group(1), match.group(2).strip()
        
        # Try simple article
        match = LegalPatterns.ARTICLE_SIMPLE.match(line)
        if match:
            return True, match.group(1), None
        
        return False, None, None
    
    @staticmethod
    def is_section_title(line: str) -> tuple[bool, str | None]:
        """
        Check if line is a section title (e.g., "1. Predmet").
        
        Returns:
            tuple: (is_section_title, title_text)
        """
        line = line.strip()
        match = LegalPatterns.SECTION_TITLE.match(line)
        if match:
            return True, match.group(1).strip()
        return False, None
    
    @staticmethod
    def is_metadata_line(line: str) -> bool:
        """
        Check if line is a metadata line (references).
        
        Returns:
            bool: True if metadata line
        """
        line = line.strip()
        return bool(LegalPatterns.METADATA_LINE.match(line))
    
    @staticmethod
    def is_paragraph(line: str) -> tuple[bool, str | None, str | None]:
        """
        Check if line is a paragraph.
        
        Returns:
            tuple: (is_paragraph, number, content)
        """
        line = line.strip()
        match = LegalPatterns.PARAGRAPH.match(line)
        if match:
            return True, match.group(1), match.group(2).strip()
        return False, None, None
    
    @staticmethod
    def is_point(line: str) -> tuple[bool, str | None, str | None]:
        """
        Check if line is a point.
        
        Returns:
            tuple: (is_point, number, content)
        """
        line = line.strip()
        match = LegalPatterns.POINT.match(line)
        if match:
            return True, match.group(1), match.group(2).strip()
        return False, None, None
    
    @staticmethod
    def is_indent(line: str) -> tuple[bool, str | None]:
        """
        Check if line is an indent.
        
        Returns:
            tuple: (is_indent, content)
        """
        line = line.strip()
        match = LegalPatterns.INDENT.match(line)
        if match:
            return True, match.group(1).strip()
        return False, None
    
    @staticmethod
    def extract_title(text: str) -> str | None:
        """
        Extract document title from text.
        
        Args:
            text: Document text
            
        Returns:
            Document title or None
        """
        lines = text.split('\n')
        title_parts = []
        found_zakon = False
        
        for line in lines[:20]:  # Check first 20 lines
            line = line.strip()
            if not line:
                continue
            
            # Check for "ZAKON"
            if LegalPatterns.TITLE_ZAKON.match(line):
                found_zakon = True
                title_parts.append(line)
                continue
            
            # Check for "o ..."
            if found_zakon:
                match = LegalPatterns.TITLE_O.match(line)
                if match:
                    title_parts.append(line)
                    break
        
        if title_parts:
            return ' '.join(title_parts)
        
        return None
    
    @staticmethod
    def extract_official_gazette(text: str) -> str | None:
        """
        Extract official gazette reference from text.
        
        Args:
            text: Document text
            
        Returns:
            Official gazette reference or None
        """
        match = LegalPatterns.OFFICIAL_GAZETTE.search(text)
        if match:
            return match.group(0)
        return None
    
    @staticmethod
    def extract_date(text: str) -> str | None:
        """
        Extract date from text (Serbian format).
        
        Args:
            text: Text containing date
            
        Returns:
            Date in ISO format (YYYY-MM-DD) or None
        """
        match = LegalPatterns.DATE_PATTERN.search(text)
        if match:
            day = match.group(1).zfill(2)
            month_name = match.group(2).lower()
            year = match.group(3)
            
            # Month name to number mapping
            months = {
                'januar': '01', 'februar': '02', 'mart': '03',
                'april': '04', 'maj': '05', 'jun': '06',
                'jul': '07', 'avgust': '08', 'septembar': '09',
                'oktobar': '10', 'novembar': '11', 'decembar': '12'
            }
            
            month = months.get(month_name)
            if month:
                return f"{year}-{month}-{day}"
        
        return None


# Convenience functions
def is_article(line: str) -> bool:
    """Check if line is an article."""
    is_art, _, _ = LegalPatterns.is_article(line)
    return is_art


def is_paragraph(line: str) -> bool:
    """Check if line is a paragraph."""
    is_para, _, _ = LegalPatterns.is_paragraph(line)
    return is_para


def is_point(line: str) -> bool:
    """Check if line is a point."""
    is_pt, _, _ = LegalPatterns.is_point(line)
    return is_pt


def is_indent(line: str) -> bool:
    """Check if line is an indent."""
    is_ind, _ = LegalPatterns.is_indent(line)
    return is_ind

# Made with Bob
