"""
Conflict Detector Service

Detects conflicts between legal proposals and existing laws using semantic search.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

from .models import (
    Conflict,
    ConflictType,
    ConflictSeverity,
    ConflictDetectionResult,
    ConflictDetectionConfig
)

logger = logging.getLogger(__name__)


class ConflictDetectorService:
    """Service for detecting conflicts between proposals and existing laws"""
    
    def __init__(self, config: ConflictDetectionConfig):
        """Initialize the conflict detector"""
        self.config = config
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {config.embedding_model}")
        self.embedding_model = SentenceTransformer(config.embedding_model)
        
        logger.info("Conflict Detector initialized")
    
    def detect_conflicts_from_proposal_result(
        self,
        proposal_result: Any  # ProposalProcessingResult
    ) -> ConflictDetectionResult:
        """
        Detect conflicts from a ProposalProcessingResult
        
        Args:
            proposal_result: Result from ProposalProcessorService
            
        Returns:
            ConflictDetectionResult with detected conflicts
        """
        start_time = datetime.now()
        
        logger.info(f"Detecting conflicts for proposal: {proposal_result.metadata.proposal_id}")
        
        conflicts = []
        documents_searched = set()
        
        # Process each legal unit in the proposal
        for unit in proposal_result.legal_units:
            unit_conflicts = self._detect_conflicts_for_unit(unit, proposal_result.metadata)
            conflicts.extend(unit_conflicts)
            
            # Track documents searched
            for conflict in unit_conflicts:
                documents_searched.add(conflict.existing_document_id)
        
        # Calculate statistics
        conflicts_by_severity = {}
        conflicts_by_type = {}
        
        for conflict in conflicts:
            # By severity
            severity_key = conflict.severity.value
            conflicts_by_severity[severity_key] = conflicts_by_severity.get(severity_key, 0) + 1
            
            # By type
            type_key = conflict.conflict_type.value
            conflicts_by_type[type_key] = conflicts_by_type.get(type_key, 0) + 1
        
        # Create result
        result = ConflictDetectionResult(
            total_conflicts=len(conflicts),
            conflicts_by_severity=conflicts_by_severity,
            conflicts_by_type=conflicts_by_type,
            conflicts=conflicts,
            proposal_id=proposal_result.metadata.proposal_id,
            proposal_title=proposal_result.metadata.title,
            documents_searched=len(documents_searched),
            processing_time_seconds=(datetime.now() - start_time).total_seconds(),
            detected_at=datetime.now().isoformat()
        )
        
        logger.info(f"Detected {len(conflicts)} conflicts across {len(documents_searched)} documents")
        
        return result
    
    def detect_conflicts_from_text(
        self,
        proposal_text: str,
        proposal_title: str = "Untitled Proposal"
    ) -> ConflictDetectionResult:
        """
        Detect conflicts from raw proposal text
        
        Args:
            proposal_text: Raw proposal text
            proposal_title: Proposal title
            
        Returns:
            ConflictDetectionResult with detected conflicts
        """
        # For basic implementation, we'll search directly
        # In production, this should go through ProposalProcessor first
        start_time = datetime.now()
        proposal_id = f"proposal_{uuid4().hex[:12]}"
        
        logger.info(f"Detecting conflicts for text proposal: {proposal_title}")
        
        # Generate embedding for the entire text
        embedding = self._generate_embedding(proposal_text)
        
        # Search for similar content
        conflicts = []
        documents_searched = set()
        
        # Search in legal_units collection
        search_results = self.client.search(
            collection_name=self.config.legal_units_collection,
            query_vector=embedding,
            limit=self.config.max_results_per_unit * 3,  # Get more results for text search
            score_threshold=self.config.similarity_threshold
        )
        
        for result in search_results:
            payload = result.payload
            similarity_score = result.score
            
            # Determine severity based on similarity
            severity = self._determine_severity(similarity_score)
            
            # Create conflict
            conflict = Conflict(
                conflict_id=str(uuid4()),
                conflict_type=ConflictType.SEMANTIC_SIMILARITY,
                severity=severity,
                proposal_unit_id=proposal_id,
                proposal_content=proposal_text[:500],  # First 500 chars
                proposal_hierarchy="N/A",
                existing_document_id=payload.get('document_id', 'unknown'),
                existing_document_title=payload.get('document_title', 'Unknown'),
                existing_unit_id=payload.get('legal_unit_id', 'unknown'),
                existing_content=payload.get('content', ''),
                existing_hierarchy=payload.get('hierarchy_path', ''),
                description=f"High semantic similarity detected ({similarity_score:.2%})",
                explanation=f"The proposal text is {similarity_score:.2%} similar to existing law: {payload.get('document_title', 'Unknown')}",
                similarity_score=similarity_score,
                recommendation="Review for potential overlap or conflict",
                detected_at=datetime.now().isoformat()
            )
            
            conflicts.append(conflict)
            documents_searched.add(payload.get('document_id', 'unknown'))
        
        # Calculate statistics
        conflicts_by_severity = {}
        conflicts_by_type = {}
        
        for conflict in conflicts:
            severity_key = conflict.severity.value
            conflicts_by_severity[severity_key] = conflicts_by_severity.get(severity_key, 0) + 1
            
            type_key = conflict.conflict_type.value
            conflicts_by_type[type_key] = conflicts_by_type.get(type_key, 0) + 1
        
        # Create result
        result = ConflictDetectionResult(
            total_conflicts=len(conflicts),
            conflicts_by_severity=conflicts_by_severity,
            conflicts_by_type=conflicts_by_type,
            conflicts=conflicts,
            proposal_id=proposal_id,
            proposal_title=proposal_title,
            documents_searched=len(documents_searched),
            processing_time_seconds=(datetime.now() - start_time).total_seconds(),
            detected_at=datetime.now().isoformat()
        )
        
        logger.info(f"Detected {len(conflicts)} conflicts")
        
        return result
    
    def _detect_conflicts_for_unit(
        self,
        unit: Dict[str, Any],
        proposal_metadata: Any
    ) -> List[Conflict]:
        """Detect conflicts for a single legal unit"""
        conflicts = []
        
        # Get unit content
        content = unit.get('content_latinized', unit.get('content', ''))
        if not content:
            return conflicts
        
        # Generate embedding
        embedding = self._generate_embedding(content)
        
        # Search for similar units
        try:
            search_results = self.client.search(
                collection_name=self.config.legal_units_collection,
                query_vector=embedding,
                limit=self.config.max_results_per_unit,
                score_threshold=self.config.similarity_threshold
            )
            
            for result in search_results:
                payload = result.payload
                similarity_score = result.score
                
                # Skip if same document (shouldn't happen, but just in case)
                if payload.get('document_id') == proposal_metadata.proposal_id:
                    continue
                
                # Determine conflict type and severity
                conflict_type = self._determine_conflict_type(unit, payload, similarity_score)
                severity = self._determine_severity(similarity_score)
                
                # Generate description and explanation
                description, explanation = self._generate_conflict_description(
                    unit, payload, conflict_type, similarity_score
                )
                
                # Create conflict
                conflict = Conflict(
                    conflict_id=str(uuid4()),
                    conflict_type=conflict_type,
                    severity=severity,
                    proposal_unit_id=unit.get('legal_unit_id', 'unknown'),
                    proposal_content=content,
                    proposal_hierarchy=unit.get('hierarchy_path', ''),
                    existing_document_id=payload.get('document_id', 'unknown'),
                    existing_document_title=payload.get('document_title', 'Unknown'),
                    existing_unit_id=payload.get('legal_unit_id', 'unknown'),
                    existing_content=payload.get('content', ''),
                    existing_hierarchy=payload.get('hierarchy_path', ''),
                    description=description,
                    explanation=explanation,
                    similarity_score=similarity_score,
                    recommendation=self._generate_recommendation(conflict_type, severity),
                    detected_at=datetime.now().isoformat()
                )
                
                conflicts.append(conflict)
        
        except Exception as e:
            logger.error(f"Error searching for conflicts: {e}")
        
        return conflicts
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def _determine_conflict_type(
        self,
        proposal_unit: Dict[str, Any],
        existing_unit: Dict[str, Any],
        similarity_score: float
    ) -> ConflictType:
        """Determine the type of conflict"""
        # For basic implementation, use semantic similarity
        # Advanced implementation would analyze normative content, etc.
        
        if similarity_score >= 0.95:
            return ConflictType.DIRECT_CONTRADICTION
        elif similarity_score >= 0.85:
            return ConflictType.NORMATIVE_CONFLICT
        else:
            return ConflictType.SEMANTIC_SIMILARITY
    
    def _determine_severity(self, similarity_score: float) -> ConflictSeverity:
        """Determine conflict severity based on similarity score"""
        if similarity_score >= self.config.critical_threshold:
            return ConflictSeverity.CRITICAL
        elif similarity_score >= self.config.high_threshold:
            return ConflictSeverity.HIGH
        elif similarity_score >= self.config.medium_threshold:
            return ConflictSeverity.MEDIUM
        else:
            return ConflictSeverity.LOW
    
    def _generate_conflict_description(
        self,
        proposal_unit: Dict[str, Any],
        existing_unit: Dict[str, Any],
        conflict_type: ConflictType,
        similarity_score: float
    ) -> tuple[str, str]:
        """Generate human-readable description and explanation"""
        existing_title = existing_unit.get('document_title', 'Unknown document')
        existing_hierarchy = existing_unit.get('hierarchy_path', 'Unknown location')
        
        if conflict_type == ConflictType.DIRECT_CONTRADICTION:
            description = f"Direct contradiction with {existing_title}"
            explanation = (
                f"The proposal content directly contradicts existing law at {existing_hierarchy}. "
                f"Similarity: {similarity_score:.2%}. This must be resolved before adoption."
            )
        elif conflict_type == ConflictType.NORMATIVE_CONFLICT:
            description = f"Normative conflict with {existing_title}"
            explanation = (
                f"The proposal creates conflicting obligations or prohibitions with existing law "
                f"at {existing_hierarchy}. Similarity: {similarity_score:.2%}."
            )
        else:
            description = f"Semantic similarity with {existing_title}"
            explanation = (
                f"The proposal has high semantic similarity ({similarity_score:.2%}) with existing law "
                f"at {existing_hierarchy}. Review for potential overlap or redundancy."
            )
        
        return description, explanation
    
    def _generate_recommendation(
        self,
        conflict_type: ConflictType,
        severity: ConflictSeverity
    ) -> str:
        """Generate recommendation for resolving conflict"""
        if severity == ConflictSeverity.CRITICAL:
            return "CRITICAL: Must be resolved before adoption. Consider explicit repeal or amendment."
        elif severity == ConflictSeverity.HIGH:
            return "HIGH: Should be resolved. Review and clarify relationship with existing law."
        elif severity == ConflictSeverity.MEDIUM:
            return "MEDIUM: Should be reviewed. Ensure consistency with existing legal framework."
        else:
            return "LOW: Informational. Review for potential overlap or redundancy."

# Made with Bob
