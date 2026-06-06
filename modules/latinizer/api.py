"""
Latinizer API.

FastAPI endpoints for Cyrillic-to-Latin text conversion.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from modules.latinizer.service import service
from modules.latinizer.database import db as db_manager
from modules.latinizer.models import LatinizerJob
from shared.config_loader import config
from shared.logger import get_module_logger

# Initialize logger
logger = get_module_logger("latinizer", config.get_log_level())

# Create FastAPI app
app = FastAPI(
    title="Latinizer API",
    description="API for converting Serbian Cyrillic text to Latin script",
    version="1.0.0"
)


# Request/Response models
class LatinizeRequest(BaseModel):
    """Request model for latinization."""
    text: str = Field(..., description="Text to latinize (may contain Cyrillic)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Закон о раду регулише права и обавезе запослених."
            }
        }


class LatinizeResponse(BaseModel):
    """Response model for latinization."""
    job_id: int = Field(..., description="Job ID")
    latinized_text: str = Field(..., description="Latinized text")
    input_length: int = Field(..., description="Length of input text")
    output_length: int = Field(..., description="Length of output text")
    cyrillic_chars_converted: int = Field(..., description="Number of Cyrillic characters converted")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(..., description="Job creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": 1,
                "latinized_text": "Zakon o radu regulise prava i obaveze zaposlenih.",
                "input_length": 52,
                "output_length": 52,
                "cyrillic_chars_converted": 45,
                "processing_time_ms": 1.23,
                "created_at": "2026-06-06T14:23:00Z"
            }
        }


class JobResponse(BaseModel):
    """Response model for job retrieval."""
    job_id: int
    input_text: str
    output_text: str
    cyrillic_chars_converted: int
    processing_time_ms: float
    created_at: datetime


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    module: str
    port: int
    timestamp: datetime


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "module": "latinizer",
        "port": config.get_module_port("latinizer"),
        "timestamp": datetime.utcnow()
    }


@app.post("/api/latinize", response_model=LatinizeResponse, status_code=status.HTTP_201_CREATED)
async def latinize_text(request: LatinizeRequest):
    """
    Convert Cyrillic text to Latin.
    
    Args:
        request: Latinization request with text
    
    Returns:
        Latinization result with job ID
    
    Raises:
        HTTPException: If latinization fails
    """
    try:
        logger.info(f"Received latinization request for {len(request.text)} characters")
        
        # Latinize text
        result = service.latinize(request.text)
        
        # Create job record
        job = LatinizerJob(
            input_text=request.text,
            output_text=result["latinized_text"],
            cyrillic_chars_converted=result["cyrillic_chars_converted"],
            processing_time_ms=result["processing_time_ms"]
        )
        
        # Save to database
        saved_job = db_manager.create(job)
        
        logger.info(f"Latinization job {saved_job.id} completed successfully")
        
        return {
            "job_id": saved_job.id,
            "latinized_text": result["latinized_text"],
            "input_length": result["input_length"],
            "output_length": result["output_length"],
            "cyrillic_chars_converted": result["cyrillic_chars_converted"],
            "processing_time_ms": result["processing_time_ms"],
            "created_at": saved_job.created_at
        }
        
    except Exception as e:
        logger.error(f"Error latinizing text: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Latinization failed: {str(e)}"
        )


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int):
    """
    Get latinization job by ID.
    
    Args:
        job_id: Job ID
    
    Returns:
        Job details
    
    Raises:
        HTTPException: If job not found
    """
    try:
        job = db_manager.get_by_id(LatinizerJob, job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        return {
            "job_id": job.id,
            "input_text": job.input_text,
            "output_text": job.output_text,
            "cyrillic_chars_converted": job.cyrillic_chars_converted,
            "processing_time_ms": job.processing_time_ms,
            "created_at": job.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job: {str(e)}"
        )


@app.get("/api/jobs", response_model=List[JobResponse])
async def list_jobs(limit: int = 10, offset: int = 0):
    """
    List latinization jobs.
    
    Args:
        limit: Maximum number of jobs to return (default: 10)
        offset: Number of jobs to skip (default: 0)
    
    Returns:
        List of jobs
    """
    try:
        jobs = db_manager.get_all(LatinizerJob, limit=limit, offset=offset)
        
        return [
            {
                "job_id": job.id,
                "input_text": job.input_text[:100] + "..." if len(job.input_text) > 100 else job.input_text,
                "output_text": job.output_text[:100] + "..." if len(job.output_text) > 100 else job.output_text,
                "cyrillic_chars_converted": job.cyrillic_chars_converted,
                "processing_time_ms": job.processing_time_ms,
                "created_at": job.created_at
            }
            for job in jobs
        ]
        
    except Exception as e:
        logger.error(f"Error listing jobs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )


@app.delete("/api/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: int):
    """
    Delete latinization job.
    
    Args:
        job_id: Job ID
    
    Raises:
        HTTPException: If job not found or deletion fails
    """
    try:
        success = db_manager.delete(LatinizerJob, job_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        logger.info(f"Deleted job {job_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}"
        )


@app.get("/api/stats")
async def get_stats():
    """
    Get latinization statistics.
    
    Returns:
        Statistics about latinization jobs
    """
    try:
        all_jobs = db_manager.get_all(LatinizerJob)
        
        if not all_jobs:
            return {
                "total_jobs": 0,
                "total_chars_processed": 0,
                "total_cyrillic_converted": 0,
                "avg_processing_time_ms": 0
            }
        
        total_chars = sum(len(job.input_text) for job in all_jobs)
        total_cyrillic = sum(job.cyrillic_chars_converted for job in all_jobs)
        avg_time = sum(job.processing_time_ms for job in all_jobs) / len(all_jobs)
        
        return {
            "total_jobs": len(all_jobs),
            "total_chars_processed": total_chars,
            "total_cyrillic_converted": total_cyrillic,
            "avg_processing_time_ms": round(avg_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

# Made with Bob
