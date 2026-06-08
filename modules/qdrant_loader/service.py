"""
Qdrant Loader Service

Handles loading legal document data from JSON exports into Qdrant vector database.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    CollectionInfo, OptimizersConfigDiff
)
from sentence_transformers import SentenceTransformer

from .models import (
    LegalUnitPayload,
    NormativeContentPayload,
    DocumentMetadataPayload,
    LoaderConfig,
    LoaderStats
)

logger = logging.getLogger(__name__)


class QdrantLoaderService:
    """Service for loading legal documents into Qdrant"""
    
    def __init__(self, config: LoaderConfig):
        """Initialize the loader service"""
        self.config = config
        self.client = QdrantClient(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {config.embedding_model}")
        self.embedding_model = SentenceTransformer(config.embedding_model)
        
        # Verify vector size matches model
        test_embedding = self.embedding_model.encode("test")
        actual_size = len(test_embedding)
        if actual_size != config.vector_size:
            logger.warning(
                f"Vector size mismatch: config={config.vector_size}, "
                f"model={actual_size}. Using model size."
            )
            self.config.vector_size = actual_size
        
        self.stats = LoaderStats()
    
    def setup_collections(self) -> None:
        """Create or recreate Qdrant collections"""
        logger.info("Setting up Qdrant collections...")
        
        collections = [
            self.config.legal_units_collection,
            self.config.normative_collection,
            self.config.metadata_collection
        ]
        
        distance = Distance.COSINE if self.config.distance_metric == "Cosine" else Distance.EUCLID
        
        for collection_name in collections:
            # Check if collection exists
            try:
                collection_info = self.client.get_collection(collection_name)
                if self.config.recreate_collections:
                    logger.info(f"Deleting existing collection: {collection_name}")
                    self.client.delete_collection(collection_name)
                else:
                    logger.info(f"Collection already exists: {collection_name}")
                    continue
            except Exception:
                pass  # Collection doesn't exist
            
            # Create collection
            logger.info(f"Creating collection: {collection_name}")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.config.vector_size,
                    distance=distance
                ),
                optimizers_config=OptimizersConfigDiff(
                    indexing_threshold=10000  # Start indexing after 10k points
                )
            )
        
        logger.info("Collections setup complete")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def load_document_from_json(self, json_path: Path) -> None:
        """Load a single document from JSON export"""
        logger.info(f"Loading document from: {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract document metadata
            doc_metadata = data.get('document_metadata', {})
            document_id = doc_metadata.get('document_id', str(uuid4()))
            
            # Load legal units
            legal_units = data.get('legal_units', [])
            self._load_legal_units(document_id, legal_units, doc_metadata)
            
            # Load normative content
            self._load_normative_content(document_id, legal_units, doc_metadata)
            
            # Load document metadata
            self._load_document_metadata(document_id, doc_metadata, legal_units)
            
            self.stats.documents_processed += 1
            logger.info(f"Successfully loaded document: {document_id}")
            
        except Exception as e:
            error_msg = f"Error loading {json_path}: {str(e)}"
            logger.error(error_msg)
            self.stats.errors.append(error_msg)
    
    def _load_legal_units(
        self,
        document_id: str,
        legal_units: List[Dict[str, Any]],
        doc_metadata: Dict[str, Any]
    ) -> None:
        """Load legal units into Qdrant"""
        if not legal_units:
            return
        
        points = []
        
        for unit in legal_units:
            try:
                # Create payload
                payload = LegalUnitPayload(
                    document_id=document_id,
                    legal_unit_id=unit['legal_unit_id'],
                    parent_legal_unit_id=unit.get('parent_legal_unit_id'),
                    document_legal_unit_id=unit.get('document_legal_unit_id', document_id),
                    unit_type=unit['unit_type'],
                    hierarchy_level=unit['hierarchy_level'],
                    hierarchy_path=unit['hierarchy_path'],
                    title=unit.get('title'),
                    content=unit['content'],
                    content_latinized=unit['content_latinized'],
                    document_title=doc_metadata.get('title', ''),
                    document_type=doc_metadata.get('document_type', ''),
                    effective_date=doc_metadata.get('effective_date'),
                    char_count=unit.get('char_count', 0),
                    word_count=unit.get('word_count', 0),
                    processed_at=doc_metadata.get('processed_at', datetime.now().isoformat())
                )
                
                # Generate embedding from latinized content
                embedding = self._generate_embedding(unit['content_latinized'])
                
                # Create point
                point = PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload=payload.model_dump()
                )
                points.append(point)
                
            except Exception as e:
                logger.error(f"Error processing legal unit {unit.get('legal_unit_id')}: {e}")
                continue
        
        # Upload in batches
        if points:
            self._upload_points_in_batches(
                self.config.legal_units_collection,
                points
            )
            self.stats.legal_units_loaded += len(points)
            logger.info(f"Loaded {len(points)} legal units")
    
    def _load_normative_content(
        self,
        document_id: str,
        legal_units: List[Dict[str, Any]],
        doc_metadata: Dict[str, Any]
    ) -> None:
        """Load normative content into Qdrant"""
        points = []
        
        for unit in legal_units:
            normative_assertions = unit.get('normative_assertions', [])
            
            for assertion in normative_assertions:
                try:
                    # Create payload
                    payload = NormativeContentPayload(
                        document_id=document_id,
                        legal_unit_id=unit['legal_unit_id'],
                        document_legal_unit_id=unit.get('document_legal_unit_id', document_id),
                        normative_type=assertion.get('type', 'unknown'),
                        normative_text=assertion.get('text', ''),
                        normative_text_latinized=assertion.get('text_latinized', ''),
                        unit_type=unit['unit_type'],
                        hierarchy_path=unit['hierarchy_path'],
                        document_title=doc_metadata.get('title', ''),
                        document_type=doc_metadata.get('document_type', ''),
                        has_conditions=len(assertion.get('conditions', [])) > 0,
                        condition_count=len(assertion.get('conditions', [])),
                        processed_at=doc_metadata.get('processed_at', datetime.now().isoformat())
                    )
                    
                    # Generate embedding from latinized normative text
                    embedding = self._generate_embedding(assertion.get('text_latinized', ''))
                    
                    # Create point
                    point = PointStruct(
                        id=str(uuid4()),
                        vector=embedding,
                        payload=payload.model_dump()
                    )
                    points.append(point)
                    
                except Exception as e:
                    logger.error(f"Error processing normative assertion: {e}")
                    continue
        
        # Upload in batches
        if points:
            self._upload_points_in_batches(
                self.config.normative_collection,
                points
            )
            self.stats.normative_content_loaded += len(points)
            logger.info(f"Loaded {len(points)} normative assertions")
    
    def _load_document_metadata(
        self,
        document_id: str,
        doc_metadata: Dict[str, Any],
        legal_units: List[Dict[str, Any]]
    ) -> None:
        """Load document metadata into Qdrant"""
        try:
            # Calculate statistics
            total_normative = sum(
                len(unit.get('normative_assertions', []))
                for unit in legal_units
            )
            
            total_conditions = sum(
                sum(len(assertion.get('conditions', [])) 
                    for assertion in unit.get('normative_assertions', []))
                for unit in legal_units
            )
            
            total_assertions = sum(
                len(unit.get('assertions', []))
                for unit in legal_units
            )
            
            # Unit type distribution
            unit_type_dist = {}
            for unit in legal_units:
                unit_type = unit['unit_type']
                unit_type_dist[unit_type] = unit_type_dist.get(unit_type, 0) + 1
            
            # Max hierarchy depth
            max_depth = max(
                (unit['hierarchy_level'] for unit in legal_units),
                default=0
            )
            
            # Create payload
            payload = DocumentMetadataPayload(
                document_id=document_id,
                document_legal_unit_id=doc_metadata.get('document_legal_unit_id', document_id),
                title=doc_metadata.get('title', ''),
                document_type=doc_metadata.get('document_type', ''),
                effective_date=doc_metadata.get('effective_date'),
                total_units=len(legal_units),
                total_normative=total_normative,
                total_conditions=total_conditions,
                total_assertions=total_assertions,
                total_chars=doc_metadata.get('total_chars', 0),
                total_words=doc_metadata.get('total_words', 0),
                max_hierarchy_depth=max_depth,
                unit_type_distribution=unit_type_dist,
                processed_at=doc_metadata.get('processed_at', datetime.now().isoformat()),
                processing_time_seconds=doc_metadata.get('processing_time_seconds')
            )
            
            # Generate embedding from document title
            embedding = self._generate_embedding(doc_metadata.get('title', ''))
            
            # Create point
            point = PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload=payload.model_dump()
            )
            
            # Upload
            self.client.upsert(
                collection_name=self.config.metadata_collection,
                points=[point]
            )
            
            self.stats.metadata_loaded += 1
            logger.info(f"Loaded document metadata for: {document_id}")
            
        except Exception as e:
            logger.error(f"Error loading document metadata: {e}")
    
    def _upload_points_in_batches(
        self,
        collection_name: str,
        points: List[PointStruct]
    ) -> None:
        """Upload points to Qdrant in batches"""
        batch_size = self.config.batch_size
        
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
            except Exception as e:
                logger.error(f"Error uploading batch to {collection_name}: {e}")
                raise
    
    def load_batch(self, json_dir: Path) -> LoaderStats:
        """Load all JSON files from a directory"""
        logger.info(f"Starting batch load from: {json_dir}")
        self.stats.start_time = datetime.now()
        
        # Find all JSON files
        json_files = list(json_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files")
        
        # Load each file
        for json_file in json_files:
            self.load_document_from_json(json_file)
        
        self.stats.end_time = datetime.now()
        logger.info(f"Batch load complete: {self.stats.to_dict()}")
        
        return self.stats
    
    def get_collection_info(self, collection_name: str) -> Optional[CollectionInfo]:
        """Get information about a collection"""
        try:
            return self.client.get_collection(collection_name)
        except Exception as e:
            logger.error(f"Error getting collection info for {collection_name}: {e}")
            return None
    
    def get_all_collections_info(self) -> Dict[str, Any]:
        """Get information about all collections"""
        info = {}
        
        for collection_name in [
            self.config.legal_units_collection,
            self.config.normative_collection,
            self.config.metadata_collection
        ]:
            collection_info = self.get_collection_info(collection_name)
            if collection_info:
                info[collection_name] = {
                    "points_count": collection_info.points_count,
                    "vectors_count": collection_info.vectors_count,
                    "indexed_vectors_count": collection_info.indexed_vectors_count,
                    "status": collection_info.status
                }
        
        return info

# Made with Bob
