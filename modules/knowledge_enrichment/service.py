"""
Knowledge Enrichment Module - Service Layer
Implements ontology matching, reference resolution, and definition extraction
Based on ZAIKON hybrid ontology approach with Stanza NER support
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import time

from .database import KnowledgeEnrichmentDatabase
from .models import (
    OntologyTerm, LegalReference, TermDefinition,
    EnrichedAssertion, EnrichmentRequest, EnrichmentResponse,
    OntologyMatchRequest, OntologyMatchResponse,
    ReferenceResolutionRequest, ReferenceResolutionResponse,
    DefinitionExtractionRequest, DefinitionExtractionResponse
)

# Global CLASSLA pipeline (lazy loaded)
_classla_pipeline = None


def _get_classla_pipeline():
    """Get or initialize CLASSLA NER pipeline for Serbian."""
    global _classla_pipeline
    if _classla_pipeline is None:
        try:
            import classla
            logger = logging.getLogger(__name__)
            logger.info("Initializing CLASSLA NER pipeline for Serbian...")
            _classla_pipeline = classla.Pipeline(
                lang='sr',
                processors='tokenize,ner',
                use_gpu=False,  # Set to True if GPU available
                verbose=False
            )
            logger.info("CLASSLA NER pipeline initialized successfully")
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to initialize CLASSLA NER: {e}. Will use entities from M7 only.")
            _classla_pipeline = False  # Mark as failed to avoid retrying
    return _classla_pipeline if _classla_pipeline is not False else None


# CLASSLA entity type mapping
CLASSLA_TYPE_MAPPING = {
    "PER": "PERSON",
    "PERSON": "PERSON",
    "ORG": "ORGANIZATION",
    "ORGANIZATION": "ORGANIZATION",
    "LOC": "LOCATION",
    "LOCATION": "LOCATION",
    "GPE": "LOCATION",
}


class OntologyMatcher:
    """
    Hybrid ontology matcher with auto-learning
    Based on ZAIKON's successful approach
    """
    
    def __init__(self, db: KnowledgeEnrichmentDatabase):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def _extract_additional_entities_with_classla(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract additional entities using CLASSLA NER
        This complements entities from M7 (CLASSLA)
        """
        additional_entities = []
        
        pipeline = _get_classla_pipeline()
        if pipeline is None:
            return additional_entities
        
        try:
            # Process text with CLASSLA
            doc = pipeline(text)  # type: ignore
            
            # Extract entities from all sentences
            if hasattr(doc, 'sentences'):
                for sentence in doc.sentences:  # type: ignore
                    if hasattr(sentence, 'ents'):
                        for entity in sentence.ents:  # type: ignore
                            entity_type = CLASSLA_TYPE_MAPPING.get(entity.type, entity.type)
                            additional_entities.append({
                                'text': entity.text,
                                'type': entity_type,
                                'start': entity.start_char if hasattr(entity, 'start_char') else 0,
                                'end': entity.end_char if hasattr(entity, 'end_char') else 0,
                                'confidence': 0.8,  # CLASSLA confidence
                                'source': 'classla'
                            })
            
            self.logger.info(f"CLASSLA found {len(additional_entities)} additional entities")
            
        except Exception as e:
            self.logger.error(f"Error in CLASSLA NER: {e}")
        
        return additional_entities
    
    def match_terms(self, text: str, entities: List[Dict[str, Any]],
                   auto_learn: bool = True, use_classla: bool = True) -> Tuple[List[Dict[str, Any]], int]:
        """
        Match text against ontology and optionally auto-learn new terms
        Uses entities from M7 (CLASSLA) + optional CLASSLA NER for additional coverage
        
        Args:
            text: Original text for additional NER analysis
            entities: Entities from M7 (CLASSLA)
            auto_learn: Whether to auto-learn new terms
            use_classla: Whether to use CLASSLA for additional entity extraction
        
        Returns:
            Tuple of (matched_terms, new_terms_learned_count)
        """
        matched_terms = []
        new_terms_learned = 0
        
        # Combine entities from M7 with additional CLASSLA entities
        all_entities = list(entities)
        if use_classla:
            classla_entities = self._extract_additional_entities_with_classla(text)
            # Add only unique entities (avoid duplicates)
            existing_texts = {e.get('text', '').lower() for e in all_entities}
            for classla_entity in classla_entities:
                if classla_entity['text'].lower() not in existing_texts:
                    all_entities.append(classla_entity)
        
        self.logger.info(f"Processing {len(all_entities)} entities ({len(entities)} from M7, {len(all_entities) - len(entities)} from CLASSLA)")
        
        # Match all entities against ontology
        for entity in all_entities:
            entity_text = entity.get('text', '').lower()
            entity_type = entity.get('type', 'UNKNOWN')
            
            # Search in ontology
            ontology_matches = self.db.search_ontology_terms(entity_text, limit=5)
            
            if ontology_matches:
                # Found existing term(s)
                best_match = ontology_matches[0]
                matched_terms.append({
                    'entity_text': entity_text,
                    'entity_type': entity_type,
                    'canonical_form': best_match.canonical_form,
                    'label': best_match.label,
                    'domain': best_match.domain,
                    'confidence': best_match.confidence,
                    'source': 'ontology'
                })
                
                # Increment frequency
                self.db.increment_term_frequency(best_match.canonical_form)
                
            elif auto_learn and entity_type in ['ORG', 'PERSON', 'LAW', 'LEGAL_TERM']:
                # Auto-learn new term from NER
                new_term = OntologyTerm(
                    canonical_form=entity_text,
                    label=entity_text,
                    domain=self._map_entity_type_to_domain(entity_type),
                    confidence=0.7,  # Lower confidence for auto-learned
                    frequency=1,
                    source='ner'
                )
                
                try:
                    self.db.add_ontology_term(new_term)
                    new_terms_learned += 1
                    
                    matched_terms.append({
                        'entity_text': entity_text,
                        'entity_type': entity_type,
                        'canonical_form': entity_text,
                        'label': entity_text,
                        'domain': new_term.domain,
                        'confidence': 0.7,
                        'source': 'auto_learned'
                    })
                    
                    self.logger.info(f"Auto-learned new term: {entity_text}")
                    
                except Exception as e:
                    self.logger.error(f"Error auto-learning term {entity_text}: {e}")
        
        return matched_terms, new_terms_learned
    
    def _map_entity_type_to_domain(self, entity_type: str) -> str:
        """Map NER entity type to legal domain"""
        mapping = {
            'ORG': 'organization',
            'PERSON': 'person',
            'LAW': 'legislation',
            'LEGAL_TERM': 'legal_concept',
            'DATE': 'temporal',
            'MONEY': 'financial'
        }
        return mapping.get(entity_type, 'general')


class ReferenceResolver:
    """
    Resolves legal references in text
    Identifies citations like "Član 5. Zakona o..."
    """
    
    def __init__(self, db: KnowledgeEnrichmentDatabase):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Reference patterns (Serbian legal citations)
        self.patterns = [
            # "Član 5. Zakona o..."
            r'[Čč]lan(?:a|u)?\s+(\d+)\.?\s+([A-ZČĆŽŠĐ][a-zčćžšđ\s]+)',
            # "Stav 2. člana 5."
            r'[Ss]tav(?:a|u)?\s+(\d+)\.?\s+[čć]lana\s+(\d+)\.',
            # "Tačka 3) stava 2."
            r'[Tt]ačk(?:a|e|u)\s+(\d+)\)?\s+stava\s+(\d+)\.',
            # "Zakon o..."
            r'([Zz]akon|[Uu]redba|[Pp]ravilnik|[Oo]dluka)\s+o\s+([a-zčćžšđ\s]+)',
            # "Službeni glasnik RS, br. 123/2020"
            r'[Ss]lužbeni\s+glasnik\s+RS,?\s+br\.?\s+(\d+/\d+)',
        ]
    
    def resolve_references(self, text: str, assertion_id: int) -> List[LegalReference]:
        """
        Extract and resolve legal references from text
        
        Returns:
            List of LegalReference objects
        """
        references = []
        
        for pattern in self.patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                raw_reference = match.group(0)
                
                # Parse reference components
                ref = self._parse_reference(raw_reference, match, assertion_id)
                
                if ref:
                    references.append(ref)
                    self.logger.debug(f"Found reference: {raw_reference}")
        
        return references
    
    def _parse_reference(self, raw_text: str, match: re.Match, 
                        assertion_id: int) -> Optional[LegalReference]:
        """Parse reference match into structured format"""
        try:
            groups = match.groups()
            
            ref = LegalReference(
                assertion_id=assertion_id,
                raw_reference=raw_text,
                document_type=None,
                document_name=None,
                article_number=None,
                paragraph_number=None,
                item_number=None,
                external_url=None,
                confidence=0.8
            )
            
            # Detect document type
            if 'zakon' in raw_text.lower():
                ref.document_type = 'zakon'
            elif 'uredba' in raw_text.lower():
                ref.document_type = 'uredba'
            elif 'pravilnik' in raw_text.lower():
                ref.document_type = 'pravilnik'
            elif 'odluka' in raw_text.lower():
                ref.document_type = 'odluka'
            
            # Extract article number
            article_match = re.search(r'[čć]lan(?:a|u)?\s+(\d+)', raw_text, re.IGNORECASE)
            if article_match:
                ref.article_number = article_match.group(1)
            
            # Extract paragraph number
            stav_match = re.search(r'stav(?:a|u)?\s+(\d+)', raw_text, re.IGNORECASE)
            if stav_match:
                ref.paragraph_number = stav_match.group(1)
            
            # Extract item number
            tacka_match = re.search(r'tačk(?:a|e|u)\s+(\d+)', raw_text, re.IGNORECASE)
            if tacka_match:
                ref.item_number = tacka_match.group(1)
            
            return ref
            
        except Exception as e:
            self.logger.error(f"Error parsing reference: {e}")
            return None


class DefinitionExtractor:
    """
    Extracts term definitions from legal text
    Identifies patterns like "X znači...", "Pod X se podrazumeva..."
    """
    
    def __init__(self, db: KnowledgeEnrichmentDatabase):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Definition patterns (Serbian)
        self.patterns = [
            # "X znači Y"
            (r'([A-ZČĆŽŠĐ][a-zčćžšđ\s]+)\s+znači\s+(.+?)(?:\.|$)', 'znači'),
            # "Pod X se podrazumeva Y"
            (r'[Pp]od\s+([a-zčćžšđ\s]+)\s+se\s+podrazumeva\s+(.+?)(?:\.|$)', 'podrazumeva'),
            # "X je Y"
            (r'([A-ZČĆŽŠĐ][a-zčćžšđ\s]+)\s+je\s+(.+?)(?:\.|$)', 'je'),
            # "X predstavlja Y"
            (r'([A-ZČĆŽŠĐ][a-zčćžšđ\s]+)\s+predstavlja\s+(.+?)(?:\.|$)', 'predstavlja'),
            # "U smislu ovog zakona, X je Y"
            (r'[Uu]\s+smislu\s+ovog\s+zakona,?\s+([a-zčćžšđ\s]+)\s+je\s+(.+?)(?:\.|$)', 'u_smislu'),
        ]
    
    def extract_definitions(self, text: str, assertion_id: int) -> List[TermDefinition]:
        """
        Extract term definitions from text
        
        Returns:
            List of TermDefinition objects
        """
        definitions = []
        
        for pattern, pattern_name in self.patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                try:
                    term = match.group(1).strip()
                    definition = match.group(2).strip()
                    
                    # Filter out very short or very long terms/definitions
                    if 3 <= len(term) <= 100 and 10 <= len(definition) <= 500:
                        defn = TermDefinition(
                            assertion_id=assertion_id,
                            term=term,
                            definition=definition,
                            definition_pattern=pattern_name,
                            confidence=0.8
                        )
                        
                        definitions.append(defn)
                        self.logger.debug(f"Found definition: {term} = {definition[:50]}...")
                        
                except Exception as e:
                    self.logger.error(f"Error extracting definition: {e}")
        
        return definitions


class KnowledgeEnrichmentService:
    """
    Main service that coordinates ontology matching, reference resolution,
    and definition extraction
    """
    
    def __init__(self, db_path: str):
        self.db = KnowledgeEnrichmentDatabase(db_path)
        self.ontology_matcher = OntologyMatcher(self.db)
        self.reference_resolver = ReferenceResolver(self.db)
        self.definition_extractor = DefinitionExtractor(self.db)
        self.logger = logging.getLogger(__name__)
    
    def enrich_assertion(self, request: EnrichmentRequest) -> EnrichmentResponse:
        """
        Enrich a single assertion with ontology, references, and definitions
        Uses entities from M7 (CLASSLA) + optional Stanza NER for additional coverage
        """
        start_time = time.time()
        
        try:
            # 1. Ontology Matching (with optional CLASSLA NER)
            matched_terms, new_terms_learned = self.ontology_matcher.match_terms(
                request.assertion_text,
                request.entities or [],
                auto_learn=True,
                use_classla=request.use_classla
            )
            
            # 2. Reference Resolution
            references = self.reference_resolver.resolve_references(
                request.assertion_text,
                request.assertion_id
            )
            
            # Save references to database
            for ref in references:
                self.db.add_legal_reference(ref)
            
            # 3. Definition Extraction
            definitions = self.definition_extractor.extract_definitions(
                request.assertion_text,
                request.assertion_id
            )
            
            # Save definitions to database
            for defn in definitions:
                self.db.add_term_definition(defn)
            
            # Create enriched assertion
            processing_time_ms = (time.time() - start_time) * 1000
            
            enriched = EnrichedAssertion(
                assertion_id=request.assertion_id,
                assertion_text=request.assertion_text,
                matched_terms=matched_terms,
                legal_references=references,
                term_definitions=definitions,
                processing_time_ms=processing_time_ms
            )
            
            # Save enrichment metadata
            self.db.save_enriched_assertion(
                request.assertion_id,
                request.assertion_text,
                len(matched_terms),
                len(references),
                len(definitions),
                processing_time_ms
            )
            
            self.logger.info(
                f"Enriched assertion {request.assertion_id}: "
                f"{len(matched_terms)} terms, {len(references)} refs, "
                f"{len(definitions)} defs in {processing_time_ms:.2f}ms"
            )
            
            return EnrichmentResponse(
                success=True,
                enriched_assertion=enriched,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Error enriching assertion {request.assertion_id}: {e}")
            
            return EnrichmentResponse(
                success=False,
                error=str(e),
                processing_time_ms=processing_time_ms
            )
    
    def match_ontology(self, request: OntologyMatchRequest) -> OntologyMatchResponse:
        """Standalone ontology matching"""
        start_time = time.time()
        
        matched_terms, new_terms_learned = self.ontology_matcher.match_terms(
            request.text,
            request.entities or [],
            request.auto_learn
        )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return OntologyMatchResponse(
            matched_terms=matched_terms,
            new_terms_learned=new_terms_learned,
            processing_time_ms=processing_time_ms
        )
    
    def resolve_references(self, request: ReferenceResolutionRequest) -> ReferenceResolutionResponse:
        """Standalone reference resolution"""
        start_time = time.time()
        
        # Use dummy assertion_id for standalone resolution
        references = self.reference_resolver.resolve_references(request.text, 0)
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return ReferenceResolutionResponse(
            references=references,
            processing_time_ms=processing_time_ms
        )
    
    def extract_definitions(self, request: DefinitionExtractionRequest) -> DefinitionExtractionResponse:
        """Standalone definition extraction"""
        start_time = time.time()
        
        # Use dummy assertion_id for standalone extraction
        definitions = self.definition_extractor.extract_definitions(request.text, 0)
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return DefinitionExtractionResponse(
            definitions=definitions,
            processing_time_ms=processing_time_ms
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enrichment statistics"""
        return self.db.get_enrichment_stats()

# Made with Bob
