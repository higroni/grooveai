"""
Knowledge Enrichment Module - Database Layer
Implements hybrid ontology storage with auto-learning capabilities
Based on ZAIKON project's successful approach
"""

import sqlite3
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging
from pathlib import Path

from .models import (
    OntologyTerm, OntologyRelationship, LegalReference, 
    TermDefinition, RelationshipType
)


class KnowledgeEnrichmentDatabase:
    """Database manager for knowledge enrichment"""
    
    def __init__(self, db_path: str):
        """Initialize database connection"""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Ontology Terms Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ontology_terms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    canonical_form TEXT NOT NULL UNIQUE,
                    label TEXT NOT NULL,
                    domain TEXT,
                    confidence REAL DEFAULT 1.0,
                    frequency INTEGER DEFAULT 1,
                    source TEXT DEFAULT 'manual',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Ontology Relationships Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ontology_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    term1_id INTEGER NOT NULL,
                    term2_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (term1_id) REFERENCES ontology_terms(id),
                    FOREIGN KEY (term2_id) REFERENCES ontology_terms(id),
                    UNIQUE(term1_id, term2_id, relationship_type)
                )
            """)
            
            # Ontology Domains Table (for term categorization)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ontology_domains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    term_id INTEGER NOT NULL,
                    domain TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    FOREIGN KEY (term_id) REFERENCES ontology_terms(id),
                    UNIQUE(term_id, domain)
                )
            """)
            
            # Legal References Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS legal_references (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assertion_id INTEGER NOT NULL,
                    raw_reference TEXT NOT NULL,
                    document_type TEXT,
                    document_name TEXT,
                    article_number TEXT,
                    paragraph_number TEXT,
                    item_number TEXT,
                    external_url TEXT,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Term Definitions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS term_definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assertion_id INTEGER NOT NULL,
                    term TEXT NOT NULL,
                    definition TEXT NOT NULL,
                    definition_pattern TEXT,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Enriched Assertions Table (audit trail)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enriched_assertions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assertion_id INTEGER NOT NULL UNIQUE,
                    assertion_text TEXT NOT NULL,
                    matched_terms_count INTEGER DEFAULT 0,
                    references_count INTEGER DEFAULT 0,
                    definitions_count INTEGER DEFAULT 0,
                    processing_time_ms REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ontology_canonical ON ontology_terms(canonical_form)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ontology_label ON ontology_terms(label)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ontology_domain ON ontology_terms(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_term1 ON ontology_relationships(term1_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_term2 ON ontology_relationships(term2_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_references_assertion ON legal_references(assertion_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_definitions_assertion ON term_definitions(assertion_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_definitions_term ON term_definitions(term)")
            
            conn.commit()
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()
    
    # ==================== ONTOLOGY TERMS ====================
    
    def add_ontology_term(self, term: OntologyTerm) -> int:
        """Add or update ontology term"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO ontology_terms (canonical_form, label, domain, confidence, frequency, source)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(canonical_form) DO UPDATE SET
                    frequency = frequency + 1,
                    confidence = MAX(confidence, excluded.confidence),
                    updated_at = CURRENT_TIMESTAMP
            """, (term.canonical_form, term.label, term.domain, term.confidence, term.frequency, term.source))
            
            term_id = cursor.lastrowid or 0
            conn.commit()
            self.logger.info(f"Added/updated ontology term: {term.canonical_form}")
            return term_id
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error adding ontology term: {e}")
            raise
        finally:
            conn.close()
    
    def get_ontology_term(self, canonical_form: str) -> Optional[OntologyTerm]:
        """Get ontology term by canonical form"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM ontology_terms WHERE canonical_form = ?
            """, (canonical_form,))
            
            row = cursor.fetchone()
            if row:
                return OntologyTerm(**dict(row))
            return None
            
        finally:
            conn.close()
    
    def search_ontology_terms(self, query: str, limit: int = 10) -> List[OntologyTerm]:
        """Search ontology terms by label or canonical form"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM ontology_terms 
                WHERE canonical_form LIKE ? OR label LIKE ?
                ORDER BY frequency DESC, confidence DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            rows = cursor.fetchall()
            return [OntologyTerm(**dict(row)) for row in rows]
            
        finally:
            conn.close()
    
    def get_terms_by_domain(self, domain: str) -> List[OntologyTerm]:
        """Get all terms in a specific domain"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM ontology_terms WHERE domain = ?
                ORDER BY frequency DESC
            """, (domain,))
            
            rows = cursor.fetchall()
            return [OntologyTerm(**dict(row)) for row in rows]
            
        finally:
            conn.close()
    
    def increment_term_frequency(self, canonical_form: str):
        """Increment usage frequency of a term"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE ontology_terms 
                SET frequency = frequency + 1, updated_at = CURRENT_TIMESTAMP
                WHERE canonical_form = ?
            """, (canonical_form,))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error incrementing term frequency: {e}")
        finally:
            conn.close()
    
    # ==================== ONTOLOGY RELATIONSHIPS ====================
    
    def add_relationship(self, rel: OntologyRelationship) -> int:
        """Add ontology relationship"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO ontology_relationships 
                (term1_id, term2_id, relationship_type, confidence)
                VALUES (?, ?, ?, ?)
            """, (rel.term1_id, rel.term2_id, rel.relationship_type.value, rel.confidence))
            
            rel_id = cursor.lastrowid or 0
            conn.commit()
            return rel_id
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error adding relationship: {e}")
            raise
        finally:
            conn.close()
    
    def get_related_terms(self, term_id: int, relationship_type: Optional[RelationshipType] = None) -> List[Tuple[OntologyTerm, str]]:
        """Get related terms for a given term"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if relationship_type:
                cursor.execute("""
                    SELECT t.*, r.relationship_type
                    FROM ontology_relationships r
                    JOIN ontology_terms t ON t.id = r.term2_id
                    WHERE r.term1_id = ? AND r.relationship_type = ?
                """, (term_id, relationship_type.value))
            else:
                cursor.execute("""
                    SELECT t.*, r.relationship_type
                    FROM ontology_relationships r
                    JOIN ontology_terms t ON t.id = r.term2_id
                    WHERE r.term1_id = ?
                """, (term_id,))
            
            rows = cursor.fetchall()
            return [(OntologyTerm(**dict(row)), row['relationship_type']) for row in rows]
            
        finally:
            conn.close()
    
    # ==================== LEGAL REFERENCES ====================
    
    def add_legal_reference(self, ref: LegalReference) -> int:
        """Add legal reference"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO legal_references 
                (assertion_id, raw_reference, document_type, document_name, 
                 article_number, paragraph_number, item_number, external_url, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ref.assertion_id, ref.raw_reference, ref.document_type, ref.document_name,
                  ref.article_number, ref.paragraph_number, ref.item_number, 
                  ref.external_url, ref.confidence))
            
            ref_id = cursor.lastrowid or 0
            conn.commit()
            return ref_id
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error adding legal reference: {e}")
            raise
        finally:
            conn.close()
    
    def get_references_by_assertion(self, assertion_id: int) -> List[LegalReference]:
        """Get all references for an assertion"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM legal_references WHERE assertion_id = ?
            """, (assertion_id,))
            
            rows = cursor.fetchall()
            return [LegalReference(**dict(row)) for row in rows]
            
        finally:
            conn.close()
    
    # ==================== TERM DEFINITIONS ====================
    
    def add_term_definition(self, defn: TermDefinition) -> int:
        """Add term definition"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO term_definitions 
                (assertion_id, term, definition, definition_pattern, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, (defn.assertion_id, defn.term, defn.definition, 
                  defn.definition_pattern, defn.confidence))
            
            defn_id = cursor.lastrowid or 0
            conn.commit()
            return defn_id
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error adding term definition: {e}")
            raise
        finally:
            conn.close()
    
    def get_definitions_by_assertion(self, assertion_id: int) -> List[TermDefinition]:
        """Get all definitions for an assertion"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM term_definitions WHERE assertion_id = ?
            """, (assertion_id,))
            
            rows = cursor.fetchall()
            return [TermDefinition(**dict(row)) for row in rows]
            
        finally:
            conn.close()
    
    def get_definition_by_term(self, term: str) -> Optional[TermDefinition]:
        """Get definition for a specific term"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM term_definitions 
                WHERE term = ?
                ORDER BY confidence DESC, created_at DESC
                LIMIT 1
            """, (term,))
            
            row = cursor.fetchone()
            if row:
                return TermDefinition(**dict(row))
            return None
            
        finally:
            conn.close()
    
    # ==================== ENRICHED ASSERTIONS ====================
    
    def save_enriched_assertion(self, assertion_id: int, assertion_text: str, 
                               matched_terms_count: int, references_count: int,
                               definitions_count: int, processing_time_ms: float):
        """Save enriched assertion metadata"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO enriched_assertions 
                (assertion_id, assertion_text, matched_terms_count, references_count, 
                 definitions_count, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (assertion_id, assertion_text, matched_terms_count, references_count,
                  definitions_count, processing_time_ms))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error saving enriched assertion: {e}")
            raise
        finally:
            conn.close()
    
    def get_enrichment_stats(self) -> Dict[str, Any]:
        """Get enrichment statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Ontology stats
            cursor.execute("SELECT COUNT(*) as count FROM ontology_terms")
            stats['total_terms'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM ontology_relationships")
            stats['total_relationships'] = cursor.fetchone()['count']
            
            # Reference stats
            cursor.execute("SELECT COUNT(*) as count FROM legal_references")
            stats['total_references'] = cursor.fetchone()['count']
            
            # Definition stats
            cursor.execute("SELECT COUNT(*) as count FROM term_definitions")
            stats['total_definitions'] = cursor.fetchone()['count']
            
            # Enriched assertions stats
            cursor.execute("SELECT COUNT(*) as count FROM enriched_assertions")
            stats['total_enriched'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT AVG(processing_time_ms) as avg_time FROM enriched_assertions")
            stats['avg_processing_time_ms'] = cursor.fetchone()['avg_time'] or 0
            
            return stats
            
        finally:
            conn.close()

# Made with Bob
