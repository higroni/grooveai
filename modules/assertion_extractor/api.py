"""
API endpoints for Assertion Extractor module.
"""

import sys
import uuid
import time
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.logger import ModuleLogger
from modules.assertion_extractor.models import (
    ExtractionRequest,
    ExtractionResponse,
    ExtractionOutput,
    ExtractionJob,
    ExtractionStats
)
from modules.assertion_extractor.service import AssertionExtractorService
from modules.assertion_extractor.database import db

# Initialize logger
logger = ModuleLogger("assertion-extractor-api")

# Initialize router
router = APIRouter()

# Initialize service
service = AssertionExtractorService()


@router.post("/api/extract", response_model=ExtractionResponse)
async def extract_assertions(request: ExtractionRequest):
    """
    Extract assertions from legal unit content.
    
    Args:
        request: ExtractionRequest with legal unit data
        
    Returns:
        ExtractionResponse with extracted assertions
    """
    try:
        logger.info(f"Extracting assertions from legal unit: {request.legal_unit.unit_id}")
        
        # Extract assertions
        start_time = time.time()
        
        output = service.extract_assertions(
            content=request.legal_unit.content,
            min_confidence=request.min_confidence
        )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Save to database
        job = ExtractionJob(
            job_id=job_id,
            legal_unit_id=request.legal_unit.unit_id,
            input_content=request.legal_unit.content,
            output_assertions=json.dumps([a.dict() for a in output.assertions], ensure_ascii=False),
            total_assertions=output.stats.total_assertions,
            processing_time_ms=processing_time_ms
        )
        
        saved_job = db.create(job)
        logger.info(f"Created extraction job {saved_job.job_id}")
        
        return ExtractionResponse(
            module="assertion-extractor",
            status="success",
            job_id=job_id,
            output=output,
            metadata={"processing_time_ms": processing_time_ms}
        )
        
    except Exception as e:
        logger.error(f"Error extracting assertions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get extraction job by ID."""
    try:
        # Query by job_id field
        with db.get_session() as session:
            job = session.query(ExtractionJob).filter(
                ExtractionJob.job_id == job_id
            ).first()
            
            if not job:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
            
            # Parse assertions
            assertions = json.loads(job.output_assertions)
            
            return {
                "job_id": job.job_id,
                "legal_unit_id": job.legal_unit_id,
                "total_assertions": job.total_assertions,
                "processing_time_ms": job.processing_time_ms,
                "created_at": job.created_at.isoformat(),
                "assertions": assertions
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/jobs")
async def list_jobs(limit: int = 10, offset: int = 0):
    """List all extraction jobs."""
    try:
        jobs = db.get_all(ExtractionJob, limit=limit, offset=offset)
        total = db.count(ExtractionJob)
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "jobs": [
                {
                    "job_id": job.job_id,
                    "legal_unit_id": job.legal_unit_id,
                    "total_assertions": job.total_assertions,
                    "processing_time_ms": job.processing_time_ms,
                    "created_at": job.created_at.isoformat()
                }
                for job in jobs
            ]
        }
        
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "module": "assertion-extractor",
        "version": "1.0.0"
    }

# Made with Bob
