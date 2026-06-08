"""
API endpoints for Assertion Extractor module.
"""

import sys
import uuid
import time
import json
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.logger import ModuleLogger
from shared.monitoring import (
    get_metrics_collector, get_health_checker
)
from modules.assertion_extractor.models import (
    ExtractionRequest,
    ExtractionResponse,
    ExtractionOutput,
    ExtractionJob,
    ExtractionStats,
    BatchExtractionRequest,
    BatchExtractionResponse,
    BatchExtractionResult
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


@router.post("/api/extract/batch", response_model=BatchExtractionResponse)
async def extract_assertions_batch(request: BatchExtractionRequest):
    """
    Extract assertions from multiple legal units in batch.
    
    This endpoint processes multiple legal units efficiently by:
    - Processing units in batches to optimize memory usage
    - Enforcing batch size limits to prevent memory exhaustion
    - Tracking detailed timing metrics for performance analysis
    - Handling errors gracefully per unit
    
    Args:
        request: BatchExtractionRequest with list of legal units
        
    Returns:
        BatchExtractionResponse with results for each unit and detailed timing
    """
    # Automatic chunking for large batches to prevent memory exhaustion
    CHUNK_SIZE = 50  # Process in chunks of 50 units
    WARN_BATCH_SIZE = 100
    
    metrics = get_metrics_collector()
    batch_start = time.time()
    
    try:
        num_units = len(request.legal_units)
        logger.info(f"Starting batch extraction for {num_units} legal units")
        
        # Warn if batch is large (will be auto-chunked)
        if num_units > WARN_BATCH_SIZE:
            num_chunks = (num_units + CHUNK_SIZE - 1) // CHUNK_SIZE
            logger.warning(f"Large batch detected: {num_units} units will be processed in {num_chunks} chunks of {CHUNK_SIZE}")
        
        # Generate batch job ID
        job_id = str(uuid.uuid4())
        
        # Timing metrics
        timings = {
            "total_ms": 0,
            "per_unit_ms": [],
            "per_chunk_ms": [],
            "db_save_ms": 0,
            "processing_ms": 0,
            "num_chunks": 0
        }
        
        results = []
        successful = 0
        failed = 0
        
        # Process in chunks to manage memory
        processing_start = time.time()
        for chunk_idx in range(0, num_units, CHUNK_SIZE):
            chunk_start = time.time()
            chunk_end = min(chunk_idx + CHUNK_SIZE, num_units)
            chunk_units = request.legal_units[chunk_idx:chunk_end]
            chunk_num = (chunk_idx // CHUNK_SIZE) + 1
            total_chunks = (num_units + CHUNK_SIZE - 1) // CHUNK_SIZE
            
            logger.info(f"Processing chunk {chunk_num}/{total_chunks} ({len(chunk_units)} units)")
            
            # Process each unit in this chunk
            for unit in chunk_units:
                unit_start = time.time()
                
                try:
                    # Extract assertions for this unit
                    output = service.extract_assertions(
                        content=unit.content,
                        min_confidence=request.min_confidence
                    )
                    
                    unit_time_ms = (time.time() - unit_start) * 1000
                    timings["per_unit_ms"].append({
                        "unit_id": unit.unit_id,
                        "time_ms": unit_time_ms
                    })
                    
                    results.append(BatchExtractionResult(
                        legal_unit_id=unit.unit_id,
                        status="success",
                        output=output,
                        error=None,
                        processing_time_ms=unit_time_ms
                    ))
                    
                    successful += 1
                    logger.debug(f"Processed unit {unit.unit_id} in {unit_time_ms:.2f}ms")
                    
                    # Record success metrics
                    metrics.record("extraction_duration_ms", unit_time_ms,
                                 {"endpoint": "/extract/batch", "status": "success"})
                    
                except Exception as e:
                    unit_time_ms = (time.time() - unit_start) * 1000
                    timings["per_unit_ms"].append({
                        "unit_id": unit.unit_id,
                        "time_ms": unit_time_ms,
                        "error": str(e)
                    })
                    
                    results.append(BatchExtractionResult(
                        legal_unit_id=unit.unit_id,
                        status="error",
                        output=None,
                        error=str(e),
                        processing_time_ms=unit_time_ms
                    ))
                    
                    failed += 1
                    logger.error(f"Error processing unit {unit.unit_id}: {str(e)}")
                    
                    # Record error metrics
                    metrics.record("extraction_duration_ms", unit_time_ms,
                                 {"endpoint": "/extract/batch", "status": "error"})
            
            # Record chunk timing
            chunk_time_ms = (time.time() - chunk_start) * 1000
            timings["per_chunk_ms"].append({
                "chunk": chunk_num,
                "units": len(chunk_units),
                "time_ms": chunk_time_ms
            })
            timings["num_chunks"] = chunk_num
            
            logger.info(f"Chunk {chunk_num}/{total_chunks} completed in {chunk_time_ms:.2f}ms")
        
        timings["processing_ms"] = (time.time() - processing_start) * 1000
        
        # Save batch job to database
        db_start = time.time()
        for idx, result in enumerate(results):
            if result.status == "success" and result.output:
                # Generate unique job_id for each unit to avoid UNIQUE constraint violations
                unique_job_id = str(uuid.uuid4())
                
                job = ExtractionJob(
                    job_id=unique_job_id,
                    legal_unit_id=result.legal_unit_id,
                    input_content=next(u.content for u in request.legal_units if u.unit_id == result.legal_unit_id),
                    output_assertions=json.dumps([a.dict() for a in result.output.assertions], ensure_ascii=False),
                    total_assertions=result.output.stats.total_assertions,
                    processing_time_ms=result.processing_time_ms
                )
                db.create(job)
        
        timings["db_save_ms"] = (time.time() - db_start) * 1000
        timings["total_ms"] = (time.time() - batch_start) * 1000
        
        # Determine overall status
        if failed == 0:
            status = "success"
        elif successful == 0:
            status = "error"
        else:
            status = "partial"
        
        # Calculate statistics
        avg_time_per_unit = timings["processing_ms"] / len(request.legal_units) if request.legal_units else 0
        total_assertions = sum(r.output.stats.total_assertions for r in results if r.output)
        
        # Record metrics
        metrics.record(
            "processing_duration_ms",
            timings["total_ms"],
            {"endpoint": "/batch", "status": status}
        )
        
        logger.info(
            f"Batch extraction complete: {successful} successful, {failed} failed, "
            f"{timings['total_ms']:.2f}ms total, {avg_time_per_unit:.2f}ms avg per unit"
        )
        
        return BatchExtractionResponse(
            module="assertion-extractor",
            status=status,
            job_id=job_id,
            results=results,
            metadata={
                "total_units": len(request.legal_units),
                "successful": successful,
                "failed": failed,
                "total_assertions": total_assertions,
                "timings": timings,
                "avg_time_per_unit_ms": avg_time_per_unit,
                "throughput_units_per_sec": len(request.legal_units) / (timings["total_ms"] / 1000) if timings["total_ms"] > 0 else 0
            }
        )
        
    except Exception as e:
        # Record error metrics
        error_time = (time.time() - batch_start) * 1000
        metrics.record(
            "processing_duration_ms",
            error_time,
            {"endpoint": "/batch", "status": "error"}
        )
        
        logger.error(f"Error in batch extraction: {str(e)}", exc_info=True)
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
async def health_check() -> Dict[str, Any]:
    """
    Enhanced health check endpoint with component status.
    
    Returns:
        Health status with database component check
    """
    health_checker = get_health_checker()
    
    # Check database connection
    try:
        total = db.count(ExtractionJob)
        health_checker.register_check(
            "database", "healthy", f"Database connection OK ({total} jobs)"
        )
    except Exception as e:
        health_checker.register_check(
            "database", "unhealthy", f"Database check failed: {str(e)}"
        )
    
    health_status = health_checker.get_status()
    return {
        "module": "assertion-extractor",
        "version": "1.0.0",
        **health_status
    }

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get performance metrics.
    
    Returns:
        Performance metrics and statistics
    """
    try:
        metrics = get_metrics_collector()
        all_metrics = metrics.get_all_metrics()
        return {
            "status": "success",
            "metrics": all_metrics,
            "module": "assertion-extractor"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
