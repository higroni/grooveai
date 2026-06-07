"""
Knowledge Enrichment Module - Database Layer
Implements hybrid ontology storage with auto-learning capabilities
Uses unified database for better performance
Based on ZAIKON project's successful approach
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from contextlib import contextmanager
import logging

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from shared.unified_database import unified_db
from shared.config_loader import config
from .models import (
    OntologyTerm, OntologyRelationship, LegalReference, 
    TermDefinition, RelationshipType
)


class Base(DeclarativeBase):
    """Base class for Knowledge Enrichment models."""
    pass


class OntologyTermDB(Base):
    """Database model for ontology terms."""
    __tablename__ = "ontology_terms"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_form: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    label: Mapped[str] = mapped_column(String, nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    frequency: Mapped[int] = mapped_column(Integer, default=1)
    source: Mapped[str] = mapped_column(String, default='manual')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OntologyRelationshipDB(Base):
    """Database model for ontology relationships."""
    __tablename__ = "ontology_relationships"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    term1_id: Mapped[int] = mapped_column(Integer, ForeignKey("ontology_terms.id"), nullable=False, index=True)
    term2_id: Mapped[int] = mapped_column(Integer, ForeignKey("ontology_terms.id"), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_term1_term2_type', 'term1_id', 'term2_id', 'relationship_type', unique=True),
    )


class LegalReferenceDB(Base):
    """Database model for legal references."""
    __tablename__ = "legal_references"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assertion_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    raw_reference: Mapped[str] = mapped_column(Text, nullable=False)
    document_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    document_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    article_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    paragraph_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    item_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TermDefinitionDB(Base):
    """Database model for term definitions."""
    __tablename__ = "term_definitions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assertion_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    term: Mapped[str] = mapped_column(String, nullable=False, index=True)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    definition_pattern: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EnrichedAssertionDB(Base):
    """Database model for enriched assertions (audit trail)."""
    __tablename__ = "enriched_assertions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assertion_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    assertion_text: Mapped[str] = mapped_column(Text, nullable=False)
    matched_terms_count: Mapped[int] = mapped_column(Integer, default=0)
    references_count: Mapped[int] = mapped_column(Integer, default=0)
    definitions_count: Mapped[int] = mapped_column(Integer, default=0)
    processing_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class KnowledgeEnrichmentDatabase:
    """Database manager for knowledge enrichment using unified database."""
    
    def __init__(self):
        """Initialize database connection with unified database."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize unified database with config
        unified_db_url = config.get_unified_database_url()
        unified_db.__init__(database_url=unified_db_url)
        
        # Register base class
        unified_db.register_base(Base)
        
        # Create tables
        unified_db.create_all_tables()
        
        self.logger.info("Knowledge Enrichment database initialized with unified database")
    
    @contextmanager
    def get_session(self):
        """Get database session from unified database."""
        with unified_db.get_session() as session:
            yield session
    
    # ==================== ONTOLOGY TERMS ====================
    
    def add_ontology_term(self, term: OntologyTerm) -> int:
        """Add or update ontology term"""
        with self.get_session() as session:
            # Check if term exists
            existing = session.query(OntologyTermDB).filter_by(
                canonical_form=term.canonical_form
            ).first()
            
            if existing:
                # Update frequency and confidence
                existing.frequency += 1
                existing.confidence = max(existing.confidence, term.confidence)
                existing.updated_at = datetime.utcnow()
                session.flush()
                term_id = existing.id
            else:
                # Create new term
                term_db = OntologyTermDB(
                    canonical_form=term.canonical_form,
                    label=term.label,
                    domain=term.domain,
                    confidence=term.confidence,
                    frequency=term.frequency,
                    source=term.source
                )
                session.add(term_db)
                session.flush()
                term_id = term_db.id
            
            self.logger.info(f"Added/updated ontology term: {term.canonical_form}")
            return term_id
    
    def get_ontology_term(self, canonical_form: str) -> Optional[OntologyTerm]:
        """Get ontology term by canonical form"""
        with self.get_session() as session:
            term_db = session.query(OntologyTermDB).filter_by(
                canonical_form=canonical_form
            ).first()
            
            if term_db:
                return OntologyTerm(
                    id=term_db.id,
                    canonical_form=term_db.canonical_form,
                    label=term_db.label,
                    domain=term_db.domain,
                    confidence=term_db.confidence,
                    frequency=term_db.frequency,
                    source=term_db.source,
                    created_at=term_db.created_at,
                    updated_at=term_db.updated_at
                )
            return None
    
    def search_ontology_terms(self, query: str, limit: int = 10) -> List[OntologyTerm]:
        """Search ontology terms by label or canonical form"""
        with self.get_session() as session:
            terms_db = session.query(OntologyTermDB).filter(
                (OntologyTermDB.canonical_form.like(f"%{query}%")) |
                (OntologyTermDB.label.like(f"%{query}%"))
            ).order_by(
                OntologyTermDB.frequency.desc(),
                OntologyTermDB.confidence.desc()
            ).limit(limit).all()
            
            return [
                OntologyTerm(
                    id=t.id,
                    canonical_form=t.canonical_form,
                    label=t.label,
                    domain=t.domain,
                    confidence=t.confidence,
                    frequency=t.frequency,
                    source=t.source,
                    created_at=t.created_at,
                    updated_at=t.updated_at
                )
                for t in terms_db
            ]
    
    def get_terms_by_domain(self, domain: str) -> List[OntologyTerm]:
        """Get all terms in a specific domain"""
        with self.get_session() as session:
            terms_db = session.query(OntologyTermDB).filter_by(
                domain=domain
            ).order_by(OntologyTermDB.frequency.desc()).all()
            
            return [
                OntologyTerm(
                    id=t.id,
                    canonical_form=t.canonical_form,
                    label=t.label,
                    domain=t.domain,
                    confidence=t.confidence,
                    frequency=t.frequency,
                    source=t.source,
                    created_at=t.created_at,
                    updated_at=t.updated_at
                )
                for t in terms_db
            ]
    
    def increment_term_frequency(self, canonical_form: str):
        """Increment usage frequency of a term"""
        with self.get_session() as session:
            term = session.query(OntologyTermDB).filter_by(
                canonical_form=canonical_form
            ).first()
            
            if term:
                term.frequency += 1
                term.updated_at = datetime.utcnow()
                session.flush()
    
    # ==================== ONTOLOGY RELATIONSHIPS ====================
    
    def add_relationship(self, rel: OntologyRelationship) -> int:
        """Add ontology relationship"""
        with self.get_session() as session:
            # Check if relationship exists
            existing = session.query(OntologyRelationshipDB).filter_by(
                term1_id=rel.term1_id,
                term2_id=rel.term2_id,
                relationship_type=rel.relationship_type.value
            ).first()
            
            if existing:
                return existing.id
            
            rel_db = OntologyRelationshipDB(
                term1_id=rel.term1_id,
                term2_id=rel.term2_id,
                relationship_type=rel.relationship_type.value,
                confidence=rel.confidence
            )
            session.add(rel_db)
            session.flush()
            return rel_db.id
    
    def get_related_terms(self, term_id: int, relationship_type: Optional[RelationshipType] = None) -> List[Tuple[OntologyTerm, str]]:
        """Get related terms for a given term"""
        with self.get_session() as session:
            query = session.query(OntologyTermDB, OntologyRelationshipDB.relationship_type).join(
                OntologyRelationshipDB,
                OntologyTermDB.id == OntologyRelationshipDB.term2_id
            ).filter(OntologyRelationshipDB.term1_id == term_id)
            
            if relationship_type:
                query = query.filter(OntologyRelationshipDB.relationship_type == relationship_type.value)
            
            results = query.all()
            
            return [
                (
                    OntologyTerm(
                        id=t.id,
                        canonical_form=t.canonical_form,
                        label=t.label,
                        domain=t.domain,
                        confidence=t.confidence,
                        frequency=t.frequency,
                        source=t.source,
                        created_at=t.created_at,
                        updated_at=t.updated_at
                    ),
                    rel_type
                )
                for t, rel_type in results
            ]
    
    # ==================== LEGAL REFERENCES ====================
    
    def add_legal_reference(self, ref: LegalReference) -> int:
        """Add legal reference"""
        with self.get_session() as session:
            ref_db = LegalReferenceDB(
                assertion_id=ref.assertion_id,
                raw_reference=ref.raw_reference,
                document_type=ref.document_type,
                document_name=ref.document_name,
                article_number=ref.article_number,
                paragraph_number=ref.paragraph_number,
                item_number=ref.item_number,
                external_url=ref.external_url,
                confidence=ref.confidence
            )
            session.add(ref_db)
            session.flush()
            return ref_db.id
    
    def get_references_by_assertion(self, assertion_id: int) -> List[LegalReference]:
        """Get all references for an assertion"""
        with self.get_session() as session:
            refs_db = session.query(LegalReferenceDB).filter_by(
                assertion_id=assertion_id
            ).all()
            
            return [
                LegalReference(
                    id=r.id,
                    assertion_id=r.assertion_id,
                    raw_reference=r.raw_reference,
                    document_type=r.document_type,
                    document_name=r.document_name,
                    article_number=r.article_number,
                    paragraph_number=r.paragraph_number,
                    item_number=r.item_number,
                    external_url=r.external_url,
                    confidence=r.confidence,
                    created_at=r.created_at
                )
                for r in refs_db
            ]
    
    # ==================== TERM DEFINITIONS ====================
    
    def add_term_definition(self, defn: TermDefinition) -> int:
        """Add term definition"""
        with self.get_session() as session:
            defn_db = TermDefinitionDB(
                assertion_id=defn.assertion_id,
                term=defn.term,
                definition=defn.definition,
                definition_pattern=defn.definition_pattern,
                confidence=defn.confidence
            )
            session.add(defn_db)
            session.flush()
            return defn_db.id
    
    def get_definitions_by_assertion(self, assertion_id: int) -> List[TermDefinition]:
        """Get all definitions for an assertion"""
        with self.get_session() as session:
            defns_db = session.query(TermDefinitionDB).filter_by(
                assertion_id=assertion_id
            ).all()
            
            return [
                TermDefinition(
                    id=d.id,
                    assertion_id=d.assertion_id,
                    term=d.term,
                    definition=d.definition,
                    definition_pattern=d.definition_pattern,
                    confidence=d.confidence,
                    created_at=d.created_at
                )
                for d in defns_db
            ]
    
    def get_definition_by_term(self, term: str) -> Optional[TermDefinition]:
        """Get definition for a specific term"""
        with self.get_session() as session:
            defn_db = session.query(TermDefinitionDB).filter_by(
                term=term
            ).order_by(
                TermDefinitionDB.confidence.desc(),
                TermDefinitionDB.created_at.desc()
            ).first()
            
            if defn_db:
                return TermDefinition(
                    id=defn_db.id,
                    assertion_id=defn_db.assertion_id,
                    term=defn_db.term,
                    definition=defn_db.definition,
                    definition_pattern=defn_db.definition_pattern,
                    confidence=defn_db.confidence,
                    created_at=defn_db.created_at
                )
            return None
    
    # ==================== ENRICHED ASSERTIONS ====================
    
    def save_enriched_assertion(self, assertion_id: int, assertion_text: str, 
                               matched_terms_count: int, references_count: int,
                               definitions_count: int, processing_time_ms: float):
        """Save enriched assertion metadata"""
        with self.get_session() as session:
            # Check if exists
            existing = session.query(EnrichedAssertionDB).filter_by(
                assertion_id=assertion_id
            ).first()
            
            if existing:
                existing.assertion_text = assertion_text
                existing.matched_terms_count = matched_terms_count
                existing.references_count = references_count
                existing.definitions_count = definitions_count
                existing.processing_time_ms = processing_time_ms
                existing.created_at = datetime.utcnow()
            else:
                enriched = EnrichedAssertionDB(
                    assertion_id=assertion_id,
                    assertion_text=assertion_text,
                    matched_terms_count=matched_terms_count,
                    references_count=references_count,
                    definitions_count=definitions_count,
                    processing_time_ms=processing_time_ms
                )
                session.add(enriched)
            
            session.flush()
    
    def get_enrichment_stats(self) -> Dict[str, Any]:
        """Get enrichment statistics"""
        with self.get_session() as session:
            stats = {}
            
            # Ontology stats
            stats['total_terms'] = session.query(OntologyTermDB).count()
            stats['total_relationships'] = session.query(OntologyRelationshipDB).count()
            
            # Reference stats
            stats['total_references'] = session.query(LegalReferenceDB).count()
            
            # Definition stats
            stats['total_definitions'] = session.query(TermDefinitionDB).count()
            
            # Enriched assertions stats
            stats['total_enriched'] = session.query(EnrichedAssertionDB).count()
            
            # Average processing time
            avg_time = session.query(EnrichedAssertionDB.processing_time_ms).filter(
                EnrichedAssertionDB.processing_time_ms.isnot(None)
            ).all()
            
            if avg_time:
                stats['avg_processing_time_ms'] = sum(t[0] for t in avg_time) / len(avg_time)
            else:
                stats['avg_processing_time_ms'] = 0
            
            return stats


# Global database instance
db = KnowledgeEnrichmentDatabase()

# Made with Bob
