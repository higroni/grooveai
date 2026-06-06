"""Legal Parser service - Akoma Ntoso compatible parsing logic."""

import sys
import os
import json
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logger import ModuleLogger
from modules.legal_parser.patterns import LegalPatterns
from modules.legal_parser.utils import (
    generate_legal_unit_id,
    generate_akoma_eid,
    build_path,
    sanitize_text,
    calculate_ordinal
)
from modules.legal_parser.schemas import (
    LegalUnit,
    Document,
    ParsingStatistics,
    ParseOutput
)


class LegalParserService:
    """
    Legal Parser service for parsing Serbian legal documents.
    Creates Akoma Ntoso-compatible data structures.
    """
    
    def __init__(self):
        """Initialize Legal Parser service."""
        self.logger = ModuleLogger("legal-parser")
        self.patterns = LegalPatterns()
    
    def parse_document(
        self,
        text: str,
        source_uri: str,
        filename: str,
        document_type: str = "law",
        language_code: str = "sr"
    ) -> ParseOutput:
        """
        Parse legal document into Akoma Ntoso-compatible structure.
        
        Args:
            text: Latinized text to parse
            source_uri: Source file path or URL
            filename: Original filename
            document_type: Document type (default: "law")
            language_code: Language code (default: "sr")
            
        Returns:
            ParseOutput with document, legal_units, and statistics
        """
        start_time = time.time()
        
        self.logger.info(f"Parsing document: {filename}")
        
        # Extract document metadata
        title = self.patterns.extract_title(text)
        official_gazette = self.patterns.extract_official_gazette(text)
        
        metadata = {}
        if official_gazette:
            metadata["official_gazette"] = official_gazette
        
        # Parse legal units
        legal_units = self._parse_legal_units(text, source_uri)
        
        # Calculate statistics
        statistics = self._calculate_statistics(legal_units)
        
        # Create document
        document = Document(
            source_uri=source_uri,
            filename=filename,
            document_type=document_type,
            title=title,
            language_code=language_code,
            metadata=metadata
        )
        
        processing_time = (time.time() - start_time) * 1000
        self.logger.info(
            f"Parsed {statistics.total_units} units in {processing_time:.2f}ms"
        )
        
        return ParseOutput(
            document=document,
            legal_units=legal_units,
            statistics=statistics
        )
    
    def _parse_legal_units(self, text: str, source_uri: str) -> list[LegalUnit]:
        """
        Parse legal units from text with improved heading and content extraction.
        
        Args:
            text: Text to parse
            source_uri: Source URI for UUID generation
            
        Returns:
            List of LegalUnit objects
        """
        lines = text.split('\n')
        legal_units = []
        
        # Current context
        current_article = None
        current_paragraph = None
        current_point = None
        
        # Ordinal counters
        article_ordinal = 0
        
        i = 0
        while i < len(lines):
            original_line = lines[i]
            line = original_line.strip()
            
            if not line:
                i += 1
                continue
            
            # Try to parse as article (use original line to preserve start-of-line context)
            is_art, number, heading = self.patterns.is_article(original_line)
            if is_art and number:
                # Look backward for section title (1-3 lines)
                section_title = None
                for lookback in range(1, min(4, i + 1)):
                    prev_line = lines[i - lookback].strip()
                    is_section, title = self.patterns.is_section_title(prev_line)
                    if is_section:
                        section_title = title
                        break
                
                # Use section title as heading if found, otherwise use inline heading
                final_heading = section_title if section_title else heading
                
                # Move to next line
                i += 1
                
                # Skip metadata line if present
                if i < len(lines) and self.patterns.is_metadata_line(lines[i].strip()):
                    i += 1
                
                # Collect content until next article or section
                content_lines = []
                while i < len(lines):
                    content_line = lines[i].strip()
                    
                    # Stop if we hit next article
                    if self.patterns.is_article(content_line)[0]:
                        break
                    
                    # Stop if we hit a new section title
                    if self.patterns.is_section_title(content_line)[0]:
                        break
                    
                    # Add non-empty lines to content
                    if content_line:
                        content_lines.append(content_line)
                    
                    i += 1
                
                # Create article with content
                article_ordinal += 1
                content_text = ' '.join(content_lines)
                
                current_article = self._create_article(
                    source_uri=source_uri,
                    number=number,
                    ordinal=article_ordinal,
                    heading=final_heading,
                    content_text=content_text
                )
                legal_units.append(current_article)
                current_paragraph = None
                current_point = None
                continue
            
            # Try to parse as paragraph
            is_para, number, content = self.patterns.is_paragraph(line)
            if is_para and number and content and current_article:
                current_paragraph = self._create_paragraph(
                    source_uri=source_uri,
                    number=number,
                    content=content,
                    parent_article=current_article
                )
                legal_units.append(current_paragraph)
                current_point = None
                continue
            
            # Try to parse as point
            is_pt, number, content = self.patterns.is_point(line)
            if is_pt and number and content and current_paragraph:
                current_point = self._create_point(
                    source_uri=source_uri,
                    number=number,
                    content=content,
                    parent_paragraph=current_paragraph
                )
                legal_units.append(current_point)
                continue
            
            # Try to parse as indent
            is_ind, content = self.patterns.is_indent(line)
            if is_ind and content and current_paragraph:
                indent = self._create_indent(
                    source_uri=source_uri,
                    content=content,
                    parent_paragraph=current_paragraph,
                    legal_units=legal_units
                )
                legal_units.append(indent)
                continue
            
            # If we have a current paragraph and line doesn't match any pattern,
            # it might be continuation of paragraph content
            if current_paragraph and not is_art and not is_para and not is_pt:
                # Append to paragraph content
                current_paragraph.content_text += " " + sanitize_text(line)
            
            # Increment counter at end of loop (only reached if no continue was hit)
            i += 1
        
        return legal_units
    
    def _create_article(
        self,
        source_uri: str,
        number: str,
        ordinal: int,
        heading: str | None,
        content_text: str = ""
    ) -> LegalUnit:
        """Create article legal unit with content."""
        path = build_path("article", number)
        legal_unit_id = generate_legal_unit_id(source_uri, path)
        akoma_eid = generate_akoma_eid("article", number)
        
        return LegalUnit(
            legal_unit_id=legal_unit_id,
            parent_legal_unit_id=None,
            unit_type="article",
            number=number,
            ordinal=ordinal,
            heading=heading,
            content_text=sanitize_text(content_text) if content_text else "",
            path=path,
            akoma_eid=akoma_eid,
            akoma_wid=None,
            metadata={}
        )
    
    def _create_paragraph(
        self,
        source_uri: str,
        number: str,
        content: str,
        parent_article: LegalUnit
    ) -> LegalUnit:
        """Create paragraph legal unit."""
        path = build_path("paragraph", number, parent_article.path)
        legal_unit_id = generate_legal_unit_id(source_uri, path)
        akoma_eid = generate_akoma_eid("paragraph", number, parent_article.akoma_eid)
        
        return LegalUnit(
            legal_unit_id=legal_unit_id,
            parent_legal_unit_id=parent_article.legal_unit_id,
            unit_type="paragraph",
            number=number,
            ordinal=int(number),
            heading=None,
            content_text=sanitize_text(content),
            path=path,
            akoma_eid=akoma_eid,
            akoma_wid=None,
            metadata={}
        )
    
    def _create_point(
        self,
        source_uri: str,
        number: str,
        content: str,
        parent_paragraph: LegalUnit
    ) -> LegalUnit:
        """Create point legal unit."""
        path = build_path("point", number, parent_paragraph.path)
        legal_unit_id = generate_legal_unit_id(source_uri, path)
        akoma_eid = generate_akoma_eid("point", number, parent_paragraph.akoma_eid)
        
        return LegalUnit(
            legal_unit_id=legal_unit_id,
            parent_legal_unit_id=parent_paragraph.legal_unit_id,
            unit_type="point",
            number=number,
            ordinal=int(number),
            heading=None,
            content_text=sanitize_text(content),
            path=path,
            akoma_eid=akoma_eid,
            akoma_wid=None,
            metadata={}
        )
    
    def _create_indent(
        self,
        source_uri: str,
        content: str,
        parent_paragraph: LegalUnit,
        legal_units: list[LegalUnit]
    ) -> LegalUnit:
        """Create indent legal unit."""
        # Calculate indent number based on existing indents in this paragraph
        indent_count = sum(
            1 for unit in legal_units
            if unit.unit_type == "indent" and unit.parent_legal_unit_id == parent_paragraph.legal_unit_id
        )
        number = str(indent_count + 1)
        
        path = build_path("indent", number, parent_paragraph.path)
        legal_unit_id = generate_legal_unit_id(source_uri, path)
        akoma_eid = generate_akoma_eid("indent", number, parent_paragraph.akoma_eid)
        
        return LegalUnit(
            legal_unit_id=legal_unit_id,
            parent_legal_unit_id=parent_paragraph.legal_unit_id,
            unit_type="indent",
            number=number,
            ordinal=int(number),
            heading=None,
            content_text=sanitize_text(content),
            path=path,
            akoma_eid=akoma_eid,
            akoma_wid=None,
            metadata={}
        )
    
    def _calculate_statistics(self, legal_units: list[LegalUnit]) -> ParsingStatistics:
        """Calculate statistics about parsed legal units."""
        total_articles = sum(1 for unit in legal_units if unit.unit_type == "article")
        total_paragraphs = sum(1 for unit in legal_units if unit.unit_type == "paragraph")
        total_points = sum(1 for unit in legal_units if unit.unit_type == "point")
        total_lists = sum(1 for unit in legal_units if unit.unit_type == "list")
        total_indents = sum(1 for unit in legal_units if unit.unit_type == "indent")
        
        return ParsingStatistics(
            total_units=len(legal_units),
            total_articles=total_articles,
            total_paragraphs=total_paragraphs,
            total_points=total_points,
            total_lists=total_lists,
            total_indents=total_indents
        )
    
    def to_canonical_json(self, parse_output: ParseOutput) -> dict:
        """
        Convert ParseOutput to canonical JSON format.
        
        Args:
            parse_output: ParseOutput object
            
        Returns:
            Canonical JSON dictionary
        """
        return {
            "document": {
                "source_uri": parse_output.document.source_uri,
                "filename": parse_output.document.filename,
                "document_type": parse_output.document.document_type,
                "title": parse_output.document.title,
                "language_code": parse_output.document.language_code,
                "metadata": parse_output.document.metadata
            },
            "legal_units": [
                {
                    "legal_unit_id": unit.legal_unit_id,
                    "parent_legal_unit_id": unit.parent_legal_unit_id,
                    "unit_type": unit.unit_type,
                    "number": unit.number,
                    "ordinal": unit.ordinal,
                    "heading": unit.heading,
                    "content_text": unit.content_text,
                    "path": unit.path,
                    "akoma_eid": unit.akoma_eid,
                    "akoma_wid": unit.akoma_wid,
                    "metadata": unit.metadata
                }
                for unit in parse_output.legal_units
            ],
            "statistics": {
                "total_units": parse_output.statistics.total_units,
                "total_articles": parse_output.statistics.total_articles,
                "total_paragraphs": parse_output.statistics.total_paragraphs,
                "total_points": parse_output.statistics.total_points,
                "total_lists": parse_output.statistics.total_lists,
                "total_indents": parse_output.statistics.total_indents
            }
        }

# Made with Bob
