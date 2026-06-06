"""Tests for Legal Parser service."""

import pytest
from modules.legal_parser.service import LegalParserService
from modules.legal_parser.patterns import LegalPatterns
from modules.legal_parser.utils import generate_legal_unit_id, generate_akoma_eid


class TestLegalParserService:
    """Test Legal Parser service."""
    
    def test_parse_simple_article(self, service, sample_article_text):
        """Test parsing simple article."""
        result = service.parse_document(
            text=sample_article_text,
            source_uri="file:///test.pdf",
            filename="test.pdf"
        )
        
        assert result.document.filename == "test.pdf"
        assert result.statistics.total_articles == 1
        assert result.statistics.total_paragraphs == 1
        assert len(result.legal_units) == 2  # 1 article + 1 paragraph
        
        # Check article
        article = result.legal_units[0]
        assert article.unit_type == "article"
        assert article.number == "1"
        assert article.heading == "Predmet zakona"
        assert article.akoma_eid == "article_1"
        
        # Check paragraph
        paragraph = result.legal_units[1]
        assert paragraph.unit_type == "paragraph"
        assert paragraph.number == "1"
        assert paragraph.parent_legal_unit_id == article.legal_unit_id
        assert "Ovim zakonom" in paragraph.content_text
    
    def test_parse_article_with_points(self, service, sample_point_text):
        """Test parsing article with points."""
        result = service.parse_document(
            text=sample_point_text,
            source_uri="file:///test.pdf",
            filename="test.pdf"
        )
        
        assert result.statistics.total_articles == 1
        assert result.statistics.total_paragraphs == 1
        assert result.statistics.total_points == 2
        assert len(result.legal_units) == 4  # 1 article + 1 paragraph + 2 points
        
        # Check points
        point1 = result.legal_units[2]
        assert point1.unit_type == "point"
        assert point1.number == "1"
        assert "zaposlene" in point1.content_text
        
        point2 = result.legal_units[3]
        assert point2.unit_type == "point"
        assert point2.number == "2"
        assert "poslodavce" in point2.content_text
    
    def test_parse_multiple_articles(self, service, sample_text):
        """Test parsing multiple articles."""
        result = service.parse_document(
            text=sample_text,
            source_uri="file:///test.pdf",
            filename="test.pdf"
        )
        
        assert result.statistics.total_articles == 2
        assert result.statistics.total_paragraphs >= 2
        assert result.statistics.total_points >= 3
        
        # Check first article
        article1 = [u for u in result.legal_units if u.unit_type == "article" and u.number == "1"][0]
        assert article1.heading == "Predmet zakona"
        
        # Check second article
        article2 = [u for u in result.legal_units if u.unit_type == "article" and u.number == "2"][0]
        assert article2.heading == "Pojmovi"
    
    def test_canonical_json_conversion(self, service, sample_article_text):
        """Test conversion to canonical JSON."""
        result = service.parse_document(
            text=sample_article_text,
            source_uri="file:///test.pdf",
            filename="test.pdf"
        )
        
        canonical = service.to_canonical_json(result)
        
        assert "document" in canonical
        assert "legal_units" in canonical
        assert "statistics" in canonical
        
        assert canonical["document"]["filename"] == "test.pdf"
        assert canonical["statistics"]["total_articles"] == 1
        assert len(canonical["legal_units"]) == 2


class TestLegalPatterns:
    """Test regex patterns."""
    
    def test_article_pattern(self):
        """Test article pattern matching - both with and without diacritics."""
        patterns = LegalPatterns()
        
        # Simple article WITH diacritics
        is_art, number, heading = patterns.is_article("Član 1.")
        assert is_art
        assert number == "1"
        assert heading is None
        
        # Simple article WITHOUT diacritics
        is_art, number, heading = patterns.is_article("Clan 1.")
        assert is_art
        assert number == "1"
        assert heading is None
        
        # Article with heading WITH diacritics
        is_art, number, heading = patterns.is_article("Član 1. Predmet zakona")
        assert is_art
        assert number == "1"
        assert heading == "Predmet zakona"
        
        # Article with heading WITHOUT diacritics
        is_art, number, heading = patterns.is_article("Clan 1. Predmet zakona")
        assert is_art
        assert number == "1"
        assert heading == "Predmet zakona"
        
        # Not an article
        is_art, _, _ = patterns.is_article("(1) Ovim zakonom")
        assert not is_art
    
    def test_paragraph_pattern(self):
        """Test paragraph pattern matching."""
        patterns = LegalPatterns()
        
        is_para, number, content = patterns.is_paragraph("(1) Ovim zakonom uredjuje se.")
        assert is_para
        assert number == "1"
        assert content == "Ovim zakonom uredjuje se."
        
        is_para, _, _ = patterns.is_paragraph("Clan 1.")
        assert not is_para
    
    def test_point_pattern(self):
        """Test point pattern matching."""
        patterns = LegalPatterns()
        
        is_pt, number, content = patterns.is_point("1) zaposlene;")
        assert is_pt
        assert number == "1"
        assert content == "zaposlene;"
        
        is_pt, _, _ = patterns.is_point("(1) Ovim zakonom")
        assert not is_pt


class TestUtils:
    """Test utility functions."""
    
    def test_generate_legal_unit_id(self):
        """Test UUID generation."""
        uuid1 = generate_legal_unit_id("file:///test.pdf", "article:1")
        uuid2 = generate_legal_unit_id("file:///test.pdf", "article:1")
        uuid3 = generate_legal_unit_id("file:///test.pdf", "article:2")
        
        # Same input produces same UUID
        assert uuid1 == uuid2
        
        # Different input produces different UUID
        assert uuid1 != uuid3
    
    def test_generate_akoma_eid(self):
        """Test Akoma Ntoso eId generation."""
        # Article
        eid = generate_akoma_eid("article", "1")
        assert eid == "article_1"
        
        # Paragraph
        eid = generate_akoma_eid("paragraph", "1", "article_1")
        assert eid == "article_1__para_1"
        
        # Point
        eid = generate_akoma_eid("point", "1", "article_1__para_1")
        assert eid == "article_1__para_1__point_1"

# Made with Bob
