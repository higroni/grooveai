"""FastAPI endpoints for Legal Parser module."""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from modules.legal_parser.service import LegalParserService
from modules.legal_parser.database import db
from modules.legal_parser.models import LegalParserJob
from modules.legal_parser.schemas import (
    ParseRequest,
    ParseResponse,
    JobResponse,
    JobListResponse,
    StatsResponse,
    HealthResponse,
    DeleteResponse
)
from shared.logger import ModuleLogger

# Initialize
app = FastAPI(title="Legal Parser API", version="1.0.0")
service = LegalParserService()
logger = ModuleLogger("legal-parser-api")


@app.post("/api/parse", response_model=ParseResponse)
async def parse_document(request: ParseRequest):
    """
    Parse legal document into Akoma Ntoso-compatible structure.
    
    Args:
        request: ParseRequest with text, source_uri, filename
        
    Returns:
        ParseResponse with parsed document and legal units
    """
    try:
        logger.info(f"Parsing document: {request.filename}")
        
        # Parse document
        import time
        start_time = time.time()
        
        parse_output = service.parse_document(
            text=request.text,
            source_uri=request.source_uri,
            filename=request.filename,
            document_type=request.document_type,
            language_code=request.language_code
        )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Convert to canonical JSON
        canonical_json = service.to_canonical_json(parse_output)
        
        # Save to database
        job = LegalParserJob(
            input_text=request.text,
            source_uri=request.source_uri,
            filename=request.filename,
            canonical_json=json.dumps(canonical_json, ensure_ascii=False),
            total_units=parse_output.statistics.total_units,
            total_articles=parse_output.statistics.total_articles,
            total_paragraphs=parse_output.statistics.total_paragraphs,
            total_points=parse_output.statistics.total_points,
            document_title=parse_output.document.title,
            document_type=parse_output.document.document_type,
            language_code=parse_output.document.language_code,
            processing_time_ms=processing_time_ms
        )
        
        saved_job = db.create(job)
        logger.info(f"Created job {saved_job.id}")
        
        return ParseResponse(
            module="legal-parser",
            status="success",
            job_id=saved_job.id,
            output=parse_output,
            metadata={"processing_time_ms": processing_time_ms}
        )
        
    except Exception as e:
        logger.error(f"Error parsing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int):
    """Get job by ID."""
    try:
        job = db.get_by_id(LegalParserJob, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Parse canonical JSON
        canonical_json = json.loads(job.canonical_json)
        
        return JobResponse(
            job_id=job.id,
            document=canonical_json["document"],
            legal_units=canonical_json["legal_units"],
            statistics=canonical_json["statistics"],
            processing_time_ms=job.processing_time_ms,
            created_at=job.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs", response_model=JobListResponse)
async def list_jobs(page: int = 1, page_size: int = 10):
    """List all jobs with pagination."""
    try:
        offset = (page - 1) * page_size
        jobs = db.get_all(LegalParserJob, limit=page_size, offset=offset)
        total = db.count(LegalParserJob)
        
        job_responses = []
        for job in jobs:
            canonical_json = json.loads(job.canonical_json)
            job_responses.append(JobResponse(
                job_id=job.id,
                document=canonical_json["document"],
                legal_units=canonical_json["legal_units"],
                statistics=canonical_json["statistics"],
                processing_time_ms=job.processing_time_ms,
                created_at=job.created_at.isoformat()
            ))
        
        return JobListResponse(
            jobs=job_responses,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/jobs/{job_id}", response_model=DeleteResponse)
async def delete_job(job_id: int):
    """Delete job by ID."""
    try:
        success = db.delete(LegalParserJob, job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        
        logger.info(f"Deleted job {job_id}")
        return DeleteResponse(message="Job deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get statistics about all jobs."""
    try:
        jobs = db.get_all(LegalParserJob)
        
        total_jobs = len(jobs)
        total_units_parsed = sum(job.total_units for job in jobs)
        total_articles = sum(job.total_articles for job in jobs)
        total_paragraphs = sum(job.total_paragraphs for job in jobs)
        total_points = sum(job.total_points for job in jobs)
        avg_processing_time_ms = (
            sum(job.processing_time_ms for job in jobs) / total_jobs
            if total_jobs > 0 else 0
        )
        
        return StatsResponse(
            total_jobs=total_jobs,
            total_units_parsed=total_units_parsed,
            total_articles=total_articles,
            total_paragraphs=total_paragraphs,
            total_points=total_points,
            avg_processing_time_ms=avg_processing_time_ms
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        module="legal-parser",
        version="1.0.0"
    )

# Made with Bob
