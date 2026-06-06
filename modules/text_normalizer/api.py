"""
FastAPI application for Text Normalizer module
Port: 8102
"""
import uuid
import json
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from modules.text_normalizer.service import TextNormalizerService
from modules.text_normalizer.database import db
from modules.text_normalizer.models import TextNormalizerJob
from shared.config_loader import config


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.get("global.log_level", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("text_normalizer")


# Pydantic models for API
class NormalizeOptions(BaseModel):
    """Options for text normalization"""
    remove_extra_whitespace: bool = Field(True, description="Remove extra spaces and tabs")
    normalize_newlines: bool = Field(True, description="Normalize newlines to single \\n")
    fix_encoding: bool = Field(True, description="Fix common encoding issues")


class NormalizeRequest(BaseModel):
    """Request model for normalizing text"""
    text: str = Field(..., description="Text to normalize")
    options: Optional[NormalizeOptions] = None


class NormalizeResponse(BaseModel):
    """Response model for text normalization"""
    module: str = "text-normalizer"
    status: str
    job_id: str
    output: Optional[dict] = None
    metadata: Optional[dict] = None
    error: Optional[str] = None


class JobResponse(BaseModel):
    """Response model for job details"""
    job_id: str
    input_text: str
    output_text: str
    changes_made: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: Optional[str] = None


# Initialize FastAPI app
app = FastAPI(
    title="Text Normalizer Module",
    description="Normalizes text by removing extra whitespace, fixing encoding, etc.",
    version="1.0.0"
)

# Initialize service
text_normalizer_service = TextNormalizerService()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "module": "text-normalizer",
        "version": "1.0.0",
        "status": "running",
        "port": config.get_module_port("text_normalizer")
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "module": "text-normalizer"
    }


@app.post("/api/normalize", response_model=NormalizeResponse)
async def normalize_text(request: NormalizeRequest):
    """
    Normalize text
    
    Args:
        request: NormalizeRequest with text and options
        
    Returns:
        NormalizeResponse with normalized text and metadata
    """
    job_id = str(uuid.uuid4())
    
    logger.info(f"[{job_id}] Starting text normalization: {len(request.text)} chars")
    
    try:
        # Normalize text
        options = request.options if request.options else NormalizeOptions()
        result = text_normalizer_service.normalize(
            request.text,
            remove_extra_whitespace=options.remove_extra_whitespace,
            normalize_newlines=options.normalize_newlines,
            fix_encoding=options.fix_encoding
        )
        
        # Create job record
        job = TextNormalizerJob(
            job_id=job_id,
            input_text=request.text,
            output_text=result["normalized_text"],
            changes_made=json.dumps(result["changes_made"]),
            processing_time_ms=result["processing_time_ms"]
        )
        
        with db.get_session() as session:
            session.add(job)
            session.commit()
        
        logger.info(f"[{job_id}] Text normalization successful: {len(result['normalized_text'])} chars")
        
        return NormalizeResponse(
            status="success",
            job_id=job_id,
            output={
                "normalized_text": result["normalized_text"],
                "changes_made": result["changes_made"]
            },
            metadata={
                "processing_time_ms": result["processing_time_ms"],
                "original_length": result["original_length"],
                "normalized_length": result["normalized_length"]
            }
        )
        
    except Exception as e:
        logger.error(f"[{job_id}] Error normalizing text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """
    Get job details by ID
    
    Args:
        job_id: Job ID
        
    Returns:
        JobResponse with job details
    """
    with db.get_session() as session:
        job = session.query(TextNormalizerJob).filter_by(job_id=job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        return JobResponse(**job.to_dict())


@app.get("/api/jobs", response_model=List[JobResponse])
async def list_jobs(limit: int = 100, offset: int = 0):
    """
    List all jobs
    
    Args:
        limit: Maximum number of jobs to return
        offset: Number of jobs to skip
        
    Returns:
        List of JobResponse
    """
    with db.get_session() as session:
        jobs = session.query(TextNormalizerJob)\
            .order_by(TextNormalizerJob.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return [JobResponse(**job.to_dict()) for job in jobs]


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job
    
    Args:
        job_id: Job ID
        
    Returns:
        Success message
    """
    with db.get_session() as session:
        job = session.query(TextNormalizerJob).filter_by(job_id=job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        session.delete(job)
        session.commit()
        
        logger.info(f"Deleted job: {job_id}")
        
        return {"status": "success", "message": f"Job {job_id} deleted"}


if __name__ == "__main__":
    import uvicorn
    
    port = config.get_module_port("text_normalizer")
    host = config.get("network.modules.text_normalizer.host", "0.0.0.0")
    
    logger.info(f"Starting Text Normalizer module on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=config.get("global.log_level", "info").lower()
    )

# Made with Bob
