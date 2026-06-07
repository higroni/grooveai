"""
REST API for Vector Store module.

Provides endpoints for generating text embeddings using BAAI/bge-m3 model.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
import json
from datetime import datetime

from modules.vector_store.service import service
from modules.vector_store.database import db
from modules.vector_store.models import EmbeddingJob
from shared.config_loader import config
from shared.logger import get_module_logger

# Initialize logger
logger = get_module_logger("vector_store", config.get_log_level())

# Create FastAPI app
app = FastAPI(
    title="GROOVE.AI - Vector Store",
    description="Generate text embeddings using BAAI/bge-m3 model",
    version="1.0.0"
)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class EmbeddingRequest(BaseModel):
    """Request model for single embedding generation."""
    text: str = Field(..., description="Text to generate embedding for", min_length=1)
    metadata: Optional[dict] = Field(None, description="Optional metadata to store with embedding")
    embedding_type: Optional[str] = Field("chunk", description="Type of embedding: assertion, document, or chunk")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "text": "Zakon o radu regulise prava i obaveze zaposlenih.",
                "metadata": {"source": "zakon_o_radu.pdf", "article": "Clan 1"},
                "embedding_type": "document"
            }]
        }
    }


class BatchEmbeddingRequest(BaseModel):
    """Request model for batch embedding generation."""
    texts: List[str] = Field(..., description="List of texts to generate embeddings for", min_length=1)
    batch_size: Optional[int] = Field(None, description="Batch size for processing", gt=0)
    metadata_list: Optional[List[dict]] = Field(None, description="Optional list of metadata (one per text)")
    embedding_type: Optional[str] = Field("chunk", description="Type of embedding: assertion, document, or chunk")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "texts": [
                    "Clan 1: Opste odredbe",
                    "Clan 2: Definicije pojmova",
                    "Clan 3: Primena zakona"
                ],
                "batch_size": 32,
                "metadata_list": [
                    {"article": "Clan 1"},
                    {"article": "Clan 2"},
                    {"article": "Clan 3"}
                ],
                "embedding_type": "document"
            }]
        }
    }


class AssertionEmbeddingRequest(BaseModel):
    """Request model for assertion embedding generation."""
    assertions: List[dict] = Field(..., description="List of classified assertions from Module 9", min_length=1)
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "assertions": [
                    {
                        "assertion_id": "assert_001",
                        "text": "Poslodavac je duzan da zaposlenom isplacuje platu.",
                        "assertion_type": "obligation",
                        "confidence": 0.95,
                        "entities": [{"type": "LEGAL_REF", "text": "Clan 104"}],
                        "conditions": [{"type": "condition", "text": "ako je zaposlen"}],
                        "article_number": "Clan 104",
                        "source_document": "zakon_o_radu.pdf"
                    }
                ]
            }]
        }
    }


class EmbeddingResponse(BaseModel):
    """Response model for embedding generation."""
    job_id: str
    output: dict
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "job_id": "emb_123e4567",
                "output": {
                    "embeddings": [0.123, -0.456, 0.789],
                    "model_name": "BAAI/bge-m3",
                    "embedding_dimension": 1024,
                    "text_length": 50,
                    "processing_time_ms": 45.23
                }
            }]
        }
    }


class JobResponse(BaseModel):
    """Response model for job details."""
    model_config = {"protected_namespaces": ()}
    
    job_id: str
    embedding_type: str
    input_text: str
    embeddings: List[float]
    model_name: str
    embedding_dimension: int
    text_length: int
    processing_time_ms: float
    embedding_metadata: Optional[dict]
    assertion_type: Optional[str]
    assertion_id: Optional[str]
    source_document: Optional[str]
    source_article: Optional[str]
    created_at: str


class JobListResponse(BaseModel):
    """Response model for job list."""
    jobs: List[JobResponse]
    total: int
    limit: int
    offset: int


class ModelInfoResponse(BaseModel):
    """Response model for model information."""
    model_config = {"protected_namespaces": ()}
    
    model_name: str
    embedding_dimension: int
    device: str
    batch_size: int
    max_seq_length: Optional[int]


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Get module information."""
    return {
        "module": "vector_store",
        "version": "1.0.0",
        "status": "running",
        "model": service.model_name,
        "embedding_dimension": service.embedding_dim,
        "device": service.device
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": service.model is not None,
        "device": service.device
    }


@app.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about the loaded model."""
    try:
        info = service.get_model_info()
        logger.info("Model info requested")
        return info
    except Exception as e:
        logger.error(f"Error getting model info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    """
    Generate embedding for a single text with optional metadata.
    
    Args:
        request: EmbeddingRequest with text, metadata, and embedding_type
    
    Returns:
        EmbeddingResponse with job_id and embedding data
    """
    try:
        # Generate job ID
        job_id = f"emb_{uuid.uuid4().hex[:8]}"
        
        logger.info(
            f"Generating {request.embedding_type} embedding for job {job_id}, "
            f"text length: {len(request.text)}"
        )
        
        # Generate embedding with metadata
        result = service.generate_embedding(request.text, request.metadata)
        
        # Extract metadata fields for quick filtering
        assertion_type = None
        assertion_id = None
        source_document = None
        source_article = None
        
        if request.metadata:
            assertion_type = request.metadata.get("assertion_type")
            assertion_id = request.metadata.get("assertion_id")
            source_document = request.metadata.get("source_document")
            source_article = request.metadata.get("article_number")
        
        # Store in database
        job = EmbeddingJob(
            job_id=job_id,
            embedding_type=request.embedding_type,
            input_text=request.text,
            text_length=len(request.text),
            model_name=result["model_name"],
            embedding_dimension=result["embedding_dimension"],
            embeddings=json.dumps(result["embeddings"]),
            processing_time_ms=result["processing_time_ms"],
            embedding_metadata=json.dumps(request.metadata) if request.metadata else None,
            assertion_type=assertion_type,
            assertion_id=assertion_id,
            source_document=source_document,
            source_article=source_article
        )
        
        db.create(job)
        
        logger.info(f"Job {job_id} completed in {result['processing_time_ms']}ms")
        
        return EmbeddingResponse(
            job_id=job_id,
            output=result
        )
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate/batch", response_model=EmbeddingResponse)
async def generate_embeddings_batch(request: BatchEmbeddingRequest):
    """
    Generate embeddings for multiple texts in batch with optional metadata.
    
    Args:
        request: BatchEmbeddingRequest with list of texts, metadata, and embedding_type
    
    Returns:
        EmbeddingResponse with job_id and batch embedding data
    """
    try:
        # Generate job ID
        job_id = f"emb_batch_{uuid.uuid4().hex[:8]}"
        
        logger.info(
            f"Generating batch {request.embedding_type} embeddings for job {job_id}, "
            f"{len(request.texts)} texts"
        )
        
        # Generate embeddings with metadata
        result = service.generate_embeddings_batch(
            request.texts,
            request.batch_size,
            request.metadata_list
        )
        
        # Store in database (store concatenated texts and all embeddings)
        combined_text = "\n---\n".join(request.texts)
        combined_metadata = json.dumps(request.metadata_list) if request.metadata_list else None
        
        job = EmbeddingJob(
            job_id=job_id,
            embedding_type=request.embedding_type,
            input_text=combined_text,
            text_length=len(combined_text),
            model_name=result["model_name"],
            embedding_dimension=result["embedding_dimension"],
            embeddings=json.dumps(result["embeddings"]),
            processing_time_ms=result["total_processing_time_ms"],
            embedding_metadata=combined_metadata
        )
        
        db.create(job)
        
        logger.info(
            f"Batch job {job_id} completed: {result['text_count']} texts in "
            f"{result['total_processing_time_ms']}ms"
        )
        
        return EmbeddingResponse(
            job_id=job_id,
            output=result
        )
        
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate/assertions", response_model=EmbeddingResponse)
async def generate_assertion_embeddings(request: AssertionEmbeddingRequest):
    """
    Generate embeddings for classified assertions with rich metadata.
    
    This endpoint is designed to receive assertions from Module 9 (Assertion Classifier)
    and generate embeddings with full metadata for vector DB storage.
    
    Args:
        request: AssertionEmbeddingRequest with list of classified assertions
    
    Returns:
        EmbeddingResponse with job_id and batch embedding data
    """
    try:
        # Generate job ID
        job_id = f"emb_assertions_{uuid.uuid4().hex[:8]}"
        
        logger.info(
            f"Generating assertion embeddings for job {job_id}, "
            f"{len(request.assertions)} assertions"
        )
        
        # Extract texts and metadata from assertions
        texts = []
        metadata_list = []
        
        for assertion in request.assertions:
            texts.append(assertion["text"])
            
            # Build rich metadata for vector DB
            metadata = {
                "assertion_id": assertion.get("assertion_id"),
                "assertion_type": assertion.get("assertion_type"),
                "confidence": assertion.get("confidence"),
                "article_number": assertion.get("article_number"),
                "source_document": assertion.get("source_document"),
                "entities": assertion.get("entities", []),
                "conditions": assertion.get("conditions", []),
                "entity_count": len(assertion.get("entities", [])),
                "condition_count": len(assertion.get("conditions", []))
            }
            metadata_list.append(metadata)
        
        # Generate embeddings with metadata
        result = service.generate_embeddings_batch(texts, batch_size=32, metadata_list=metadata_list)
        
        # Add metadata to result
        result["metadata_list"] = metadata_list
        result["assertion_count"] = len(request.assertions)
        
        # Store in database (store concatenated texts and all embeddings)
        combined_text = "\n---\n".join(texts)
        combined_metadata = json.dumps(metadata_list)
        
        job = EmbeddingJob(
            job_id=job_id,
            embedding_type="assertion",
            input_text=combined_text,
            text_length=len(combined_text),
            model_name=result["model_name"],
            embedding_dimension=result["embedding_dimension"],
            embeddings=json.dumps(result["embeddings"]),
            processing_time_ms=result["total_processing_time_ms"],
            embedding_metadata=combined_metadata
        )
        
        db.create(job)
        
        logger.info(
            f"Assertion embedding job {job_id} completed: {len(request.assertions)} assertions in "
            f"{result['total_processing_time_ms']}ms"
        )
        
        return EmbeddingResponse(
            job_id=job_id,
            output=result
        )
        
    except Exception as e:
        logger.error(f"Error generating assertion embeddings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """
    Get details of a specific job.
    
    Args:
        job_id: Job identifier
    
    Returns:
        JobResponse with job details
    """
    try:
        job = db.get_by_job_id(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return JobResponse(
            job_id=job.job_id,
            embedding_type=job.embedding_type,
            input_text=job.input_text,
            embeddings=json.loads(job.embeddings),
            model_name=job.model_name,
            embedding_dimension=job.embedding_dimension,
            text_length=job.text_length,
            processing_time_ms=job.processing_time_ms,
            embedding_metadata=json.loads(job.embedding_metadata) if job.embedding_metadata else None,
            assertion_type=job.assertion_type,
            assertion_id=job.assertion_id,
            source_document=job.source_document,
            source_article=job.source_article,
            created_at=job.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs", response_model=JobListResponse)
async def list_jobs(limit: int = 10, offset: int = 0):
    """
    List all embedding jobs with pagination.
    
    Args:
        limit: Maximum number of jobs to return
        offset: Number of jobs to skip
    
    Returns:
        JobListResponse with list of jobs
    """
    try:
        jobs = db.get_all(EmbeddingJob, limit=limit, offset=offset)
        total = db.count(EmbeddingJob)
        
        job_responses = [
            JobResponse(
                job_id=job.job_id,
                embedding_type=job.embedding_type,
                input_text=job.input_text[:100] + "..." if len(job.input_text) > 100 else job.input_text,
                embeddings=json.loads(job.embeddings)[:5],  # Only first 5 values for list
                model_name=job.model_name,
                embedding_dimension=job.embedding_dimension,
                text_length=job.text_length,
                processing_time_ms=job.processing_time_ms,
                embedding_metadata=json.loads(job.embedding_metadata) if job.embedding_metadata else None,
                assertion_type=job.assertion_type,
                assertion_id=job.assertion_id,
                source_document=job.source_document,
                source_article=job.source_article,
                created_at=job.created_at.isoformat()
            )
            for job in jobs
        ]
        
        return JobListResponse(
            jobs=job_responses,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listing jobs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a specific job.
    
    Args:
        job_id: Job identifier
    
    Returns:
        Success message
    """
    try:
        deleted = db.delete_by_job_id(job_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        logger.info(f"Job {job_id} deleted")
        
        return {"message": f"Job {job_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = config.get_module_port("vector_store")
    logger.info(f"Starting Vector Store API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

# Made with Bob

