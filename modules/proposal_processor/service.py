"""
Proposal Processor Service

Processes legal proposal documents through the same pipeline as existing laws.
"""

import logging
import requests
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from .models import ProposalInput, ProposalProcessingResult, ProposalMetadata

logger = logging.getLogger(__name__)


class ProposalProcessorService:
    """Service for processing legal proposals"""
    
    def __init__(
        self,
        file_reader_url: str = "http://localhost:8001",
        text_normalizer_url: str = "http://localhost:8002",
        legal_parser_url: str = "http://localhost:8003",
        normative_extractor_url: str = "http://localhost:8006",
        condition_extractor_url: str = "http://localhost:8008",
        assertion_extractor_url: str = "http://localhost:8010"
    ):
        """Initialize the proposal processor"""
        self.file_reader_url = file_reader_url
        self.text_normalizer_url = text_normalizer_url
        self.legal_parser_url = legal_parser_url
        self.normative_extractor_url = normative_extractor_url
        self.condition_extractor_url = condition_extractor_url
        self.assertion_extractor_url = assertion_extractor_url
    
    def process_proposal(self, proposal_input: ProposalInput) -> ProposalProcessingResult:
        """
        Process a legal proposal through the full pipeline
        
        Args:
            proposal_input: Proposal input specification
            
        Returns:
            ProposalProcessingResult with processed data
        """
        start_time = datetime.now()
        proposal_id = f"proposal_{uuid4().hex[:12]}"
        
        logger.info(f"Processing proposal: {proposal_id}")
        logger.info(f"Source type: {proposal_input.source_type}")
        
        errors = []
        warnings = []
        
        try:
            # Step 1: Extract text from source
            raw_text = self._extract_text(proposal_input)
            
            if not raw_text or len(raw_text.strip()) < 100:
                raise ValueError("Extracted text is too short or empty")
            
            # Step 2: Normalize text (latinize)
            latinized_text = self._normalize_text(raw_text)
            
            # Step 3: Parse legal structure
            legal_units = self._parse_legal_structure(latinized_text, proposal_id)
            
            # Step 4: Extract normative content
            legal_units = self._extract_normative_content(legal_units)
            
            # Step 5: Extract conditions
            legal_units = self._extract_conditions(legal_units)
            
            # Step 6: Extract assertions
            legal_units = self._extract_assertions(legal_units)
            
            # Calculate statistics
            total_chars = len(raw_text)
            total_words = len(raw_text.split())
            total_units = len(legal_units)
            total_normative = sum(
                len(unit.get('normative_assertions', []))
                for unit in legal_units
            )
            
            # Auto-detect title if not provided
            title = proposal_input.title
            if not title:
                title = self._extract_title(raw_text, legal_units)
            
            # Create metadata
            metadata = ProposalMetadata(
                proposal_id=proposal_id,
                title=title,
                document_type=proposal_input.document_type,
                author=proposal_input.author,
                submission_date=proposal_input.submission_date,
                processed_at=datetime.now().isoformat(),
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                source_type=proposal_input.source_type,
                source=proposal_input.source if proposal_input.source_type != "text" else "direct_input",
                total_chars=total_chars,
                total_words=total_words,
                total_units=total_units,
                total_normative=total_normative
            )
            
            # Create result
            result = ProposalProcessingResult(
                metadata=metadata,
                legal_units=legal_units,
                raw_text=raw_text,
                latinized_text=latinized_text,
                success=True,
                errors=errors,
                warnings=warnings
            )
            
            logger.info(f"Successfully processed proposal: {proposal_id}")
            logger.info(f"  Units: {total_units}, Normative: {total_normative}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing proposal: {e}", exc_info=True)
            errors.append(str(e))
            
            # Return partial result
            return ProposalProcessingResult(
                metadata=ProposalMetadata(
                    proposal_id=proposal_id,
                    title=proposal_input.title or "Unknown",
                    document_type=proposal_input.document_type,
                    author=proposal_input.author,
                    submission_date=proposal_input.submission_date,
                    processed_at=datetime.now().isoformat(),
                    processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                    source_type=proposal_input.source_type,
                    source=proposal_input.source if proposal_input.source_type != "text" else "direct_input",
                    total_chars=0,
                    total_words=0,
                    total_units=0,
                    total_normative=0
                ),
                legal_units=[],
                raw_text="",
                latinized_text="",
                success=False,
                errors=errors,
                warnings=warnings
            )
    
    def _extract_text(self, proposal_input: ProposalInput) -> str:
        """Extract text from source"""
        logger.info("Step 1: Extracting text...")
        
        if proposal_input.source_type == "text":
            # Direct text input
            return proposal_input.source
        
        elif proposal_input.source_type == "file":
            # File path
            file_path = Path(proposal_input.source)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Call file reader service
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                response = requests.post(
                    f"{self.file_reader_url}/extract",
                    files=files,
                    timeout=120
                )
            
            if response.status_code != 200:
                raise Exception(f"File reader failed: {response.text}")
            
            result = response.json()
            return result.get('text', '')
        
        elif proposal_input.source_type == "url":
            # Download from URL
            response = requests.get(proposal_input.source, timeout=30)
            response.raise_for_status()
            
            # Save to temp file and process
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            
            try:
                with open(tmp_path, 'rb') as f:
                    files = {'file': ('document.pdf', f, 'application/pdf')}
                    response = requests.post(
                        f"{self.file_reader_url}/extract",
                        files=files,
                        timeout=120
                    )
                
                if response.status_code != 200:
                    raise Exception(f"File reader failed: {response.text}")
                
                result = response.json()
                return result.get('text', '')
            finally:
                Path(tmp_path).unlink(missing_ok=True)
        
        else:
            raise ValueError(f"Unknown source type: {proposal_input.source_type}")
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text (latinize)"""
        logger.info("Step 2: Normalizing text...")
        
        response = requests.post(
            f"{self.text_normalizer_url}/normalize",
            json={"text": text},
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Text normalizer failed: {response.text}")
        
        result = response.json()
        return result.get('latinized_text', text)
    
    def _parse_legal_structure(self, text: str, document_id: str) -> list:
        """Parse legal structure"""
        logger.info("Step 3: Parsing legal structure...")
        
        response = requests.post(
            f"{self.legal_parser_url}/parse",
            json={
                "text": text,
                "document_id": document_id
            },
            timeout=180
        )
        
        if response.status_code != 200:
            raise Exception(f"Legal parser failed: {response.text}")
        
        result = response.json()
        return result.get('legal_units', [])
    
    def _extract_normative_content(self, legal_units: list) -> list:
        """Extract normative content"""
        logger.info("Step 4: Extracting normative content...")
        
        response = requests.post(
            f"{self.normative_extractor_url}/extract",
            json={"legal_units": legal_units},
            timeout=180
        )
        
        if response.status_code != 200:
            logger.warning(f"Normative extractor failed: {response.text}")
            return legal_units
        
        result = response.json()
        return result.get('legal_units', legal_units)
    
    def _extract_conditions(self, legal_units: list) -> list:
        """Extract conditions"""
        logger.info("Step 5: Extracting conditions...")
        
        response = requests.post(
            f"{self.condition_extractor_url}/extract",
            json={"legal_units": legal_units},
            timeout=180
        )
        
        if response.status_code != 200:
            logger.warning(f"Condition extractor failed: {response.text}")
            return legal_units
        
        result = response.json()
        return result.get('legal_units', legal_units)
    
    def _extract_assertions(self, legal_units: list) -> list:
        """Extract assertions"""
        logger.info("Step 6: Extracting assertions...")
        
        response = requests.post(
            f"{self.assertion_extractor_url}/extract",
            json={"legal_units": legal_units},
            timeout=180
        )
        
        if response.status_code != 200:
            logger.warning(f"Assertion extractor failed: {response.text}")
            return legal_units
        
        result = response.json()
        return result.get('legal_units', legal_units)
    
    def _extract_title(self, raw_text: str, legal_units: list) -> str:
        """Extract title from text or legal units"""
        # Try to find title in first legal unit
        if legal_units and legal_units[0].get('title'):
            return legal_units[0]['title']
        
        # Try to extract from first lines of text
        lines = raw_text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                # Likely a title
                if any(keyword in line.lower() for keyword in ['zakon', 'uredba', 'pravilnik', 'odluka']):
                    return line
        
        # Default
        return "Predlog zakona"

# Made with Bob
