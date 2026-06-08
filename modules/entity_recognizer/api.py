"""
FastAPI endpoints for Entity Recognizer module.
"""

import json
import uuid
import time
import logging
from datetime import datetime
from typing import Dict, Any

# Initialize logger
logger = logging.getLogger(__name__)
from fastapi import APIRouter, HTTPException
from modules.entity_recognizer.models import (
    RecognitionRequest,
    RecognitionResponse,
    RecognitionJob,
    EntityDB,
    BatchRecognitionRequest,
    BatchRecognitionResponse,
    BatchRecognitionResult
)
from modules.entity_recognizer import service
from modules.entity_recognizer.database import db
from shared.monitoring import (
    get_metrics_collector, get_health_checker,
    PerformanceTimer
)

router = APIRouter()


@router.post("/api/recognize", response_model=RecognitionResponse)
async def recognize_entities(request: RecognitionRequest) -> RecognitionResponse:
    """
    Recognize entities in an assertion.
    
    Args:
        request: Recognition request with assertion data
    
    Returns:
        RecognitionResponse with recognized entities
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Perform entity recognition
        output = service.recognize_entities(
            text=request.assertion.text,
            min_confidence=request.min_confidence,
            entity_types=request.entity_types,
            use_ner=request.use_ner
        )
        
        # Store job in database
        job = RecognitionJob(
            job_id=job_id,
            assertion_id=request.assertion.assertion_id,
            assertion_text=request.assertion.text,
            output_entities=json.dumps([e.model_dump() for e in output.entities]),
            total_entities=output.stats.total_entities,
            avg_confidence=output.stats.avg_confidence,
            language=request.language,
            created_at=datetime.utcnow()
        )
        
        saved_job = db.create(job)
        
        # Store individual entities in entities table
        with db.get_session() as session:
            for entity in output.entities:
                entity_db = EntityDB(
                    entity_id=entity.entity_id,
                    job_id=job_id,
                    entity_type=entity.entity_type,
                    text=entity.text,
                    start_char=entity.start_char,
                    end_char=entity.end_char,
                    confidence=entity.confidence,
                    metadata_json=json.dumps(entity.metadata) if entity.metadata else None,
                    created_at=datetime.utcnow()
                )
                session.add(entity_db)
            session.commit()
        
        # Return response
        return RecognitionResponse(
            job_id=saved_job.job_id,
            assertion_id=request.assertion.assertion_id,
            entities=output.entities,
            stats=output.stats,
            timestamp=saved_job.created_at
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def cleanup_gpu_memory():
    """Release GPU memory after batch processing to prevent memory leaks."""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            logger.debug("GPU memory cleaned up")
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Error cleaning GPU memory: {e}")


@router.post("/api/recognize/batch", response_model=BatchRecognitionResponse)
async def recognize_entities_batch(request: BatchRecognitionRequest) -> BatchRecognitionResponse:
    """
    Recognize entities in multiple assertions in batch.
    
    This endpoint processes multiple assertions efficiently by:
    - Initializing CLASSLA NER model once for all assertions (if use_ner=True)
    - Processing assertions in batches to optimize memory usage
    - Tracking detailed timing metrics for performance analysis
    - Handling errors gracefully per assertion
    - Cleaning up GPU memory after processing to prevent leaks
    
    Args:
        request: BatchRecognitionRequest with list of assertions
        
    Returns:
        BatchRecognitionResponse with results for each assertion and detailed timing
    """
    try:
        batch_start = time.time()
        logger.info(f"Starting batch entity recognition for {len(request.assertions)} assertions (use_ner={request.use_ner})")
        
        # Generate batch job ID
        job_id = str(uuid.uuid4())
        
        # Get metrics collector
        metrics = get_metrics_collector()
        
        # Timing metrics
        timings = {
            "total_ms": 0,
            "ner_init_ms": 0,
            "processing_ms": 0,
            "db_save_ms": 0,
            "per_assertion_ms": []
        }
        
        # Pre-initialize CLASSLA if needed (CRITICAL OPTIMIZATION)
        ner_init_start = time.time()
        if request.use_ner:
            from modules.entity_recognizer.service import _get_classla_pipeline
            pipeline = _get_classla_pipeline()
            if pipeline:
                logger.info("CLASSLA NER pipeline pre-initialized for batch processing")
            else:
                logger.warning("CLASSLA NER not available, falling back to regex")
                request.use_ner = False
        timings["ner_init_ms"] = (time.time() - ner_init_start) * 1000
        
        results = []
        successful = 0
        failed = 0
        
        # Process each assertion
        processing_start = time.time()
        for assertion in request.assertions:
            assertion_start = time.time()
            
            try:
                # Recognize entities for this assertion
                output = service.recognize_entities(
                    text=assertion.text,
                    min_confidence=request.min_confidence,
                    entity_types=request.entity_types,
                    use_ner=request.use_ner
                )
                
                assertion_time_ms = (time.time() - assertion_start) * 1000
                timings["per_assertion_ms"].append({
                    "assertion_id": assertion.assertion_id,
                    "time_ms": assertion_time_ms,
                    "entities_found": output.stats.total_entities
                })
                
                results.append(BatchRecognitionResult(
                    assertion_id=assertion.assertion_id,
                    status="success",
                    output=output,
                    error=None,
                    processing_time_ms=assertion_time_ms
                ))
                
                successful += 1
                logger.debug(f"Processed assertion {assertion.assertion_id} in {assertion_time_ms:.2f}ms ({output.stats.total_entities} entities)")
                
                # Record metrics
                metrics.record("recognition_duration_ms", assertion_time_ms,
                             {"endpoint": "/recognize/batch", "status": "success"})
                
            except Exception as e:
                assertion_time_ms = (time.time() - assertion_start) * 1000
                timings["per_assertion_ms"].append({
                    "assertion_id": assertion.assertion_id,
                    "time_ms": assertion_time_ms,
                    "error": str(e)
                })
                
                results.append(BatchRecognitionResult(
                    assertion_id=assertion.assertion_id,
                    status="error",
                    output=None,
                    error=str(e),
                    processing_time_ms=assertion_time_ms
                ))
                
                failed += 1
                logger.error(f"Error processing assertion {assertion.assertion_id}: {str(e)}")
                
                # Record error metrics
                metrics.record("recognition_duration_ms", assertion_time_ms,
                             {"endpoint": "/recognize/batch", "status": "error"})
        
        timings["processing_ms"] = (time.time() - processing_start) * 1000
        
        # Save batch results to database
        db_start = time.time()
        with db.get_session() as session:
            for result in results:
                if result.status == "success" and result.output:
                    # Save job
                    job = RecognitionJob(
                        job_id=f"{job_id}_{result.assertion_id}",
                        assertion_id=result.assertion_id,
                        assertion_text=next(a.text for a in request.assertions if a.assertion_id == result.assertion_id),
                        output_entities=json.dumps([e.model_dump() for e in result.output.entities]),
                        total_entities=result.output.stats.total_entities,
                        avg_confidence=result.output.stats.avg_confidence,
                        language=request.language,
                        created_at=datetime.utcnow()
                    )
                    session.add(job)
                    
                    # Save individual entities
                    for entity in result.output.entities:
                        entity_db = EntityDB(
                            entity_id=entity.entity_id,
                            job_id=f"{job_id}_{result.assertion_id}",
                            entity_type=entity.entity_type,
                            text=entity.text,
                            start_char=entity.start_char,
                            end_char=entity.end_char,
                            confidence=entity.confidence,
                            metadata_json=json.dumps(entity.metadata) if entity.metadata else None,
                            created_at=datetime.utcnow()
                        )
                        session.add(entity_db)
            
            session.commit()
        
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
        avg_time_per_assertion = timings["processing_ms"] / len(request.assertions) if request.assertions else 0
        total_entities = sum(r.output.stats.total_entities for r in results if r.output)
        
        logger.info(
            f"Batch recognition complete: {successful} successful, {failed} failed, "
            f"{timings['total_ms']:.2f}ms total, {avg_time_per_assertion:.2f}ms avg per assertion, "
            f"NER init: {timings['ner_init_ms']:.2f}ms"
        )
        
        return BatchRecognitionResponse(
            module="entity-recognizer",
            status=status,
            job_id=job_id,
            results=results,
            metadata={
                "total_assertions": len(request.assertions),
                "successful": successful,
                "failed": failed,
                "total_entities": total_entities,
                "use_ner": request.use_ner,
                "timings": timings,
                "avg_time_per_assertion_ms": avg_time_per_assertion,
                "throughput_assertions_per_sec": len(request.assertions) / (timings["total_ms"] / 1000) if timings["total_ms"] > 0 else 0,
                "ner_overhead_percent": (timings["ner_init_ms"] / timings["total_ms"] * 100) if timings["total_ms"] > 0 else 0
            }
        )
        
    except Exception as e:
        logger.error(f"Error in batch entity recognition: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch entity recognition failed: {str(e)}")
    finally:
        # Always cleanup GPU memory after batch processing
        cleanup_gpu_memory()


@router.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """
    Get recognition job by ID.
    
    Args:
        job_id: Recognition job ID
    
    Returns:
        Job details with entities
    """
    try:
        with db.get_session() as session:
            job = session.query(RecognitionJob).filter(RecognitionJob.job_id == job_id).first()
            
            if not job:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
            
            return {
                "job_id": job.job_id,
                "assertion_id": job.assertion_id,
                "assertion_text": job.assertion_text,
                "entities": json.loads(job.output_entities),
                "total_entities": job.total_entities,
                "avg_confidence": job.avg_confidence,
                "language": job.language,
                "created_at": job.created_at.isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job: {str(e)}")


@router.get("/api/jobs")
async def list_jobs(limit: int = 50, offset: int = 0):
    """
    List all recognition jobs.
    
    Args:
        limit: Maximum number of jobs to return
        offset: Offset for pagination
    
    Returns:
        List of jobs
    """
    try:
        with db.get_session() as session:
            jobs = session.query(RecognitionJob)\
                .order_by(RecognitionJob.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            total = session.query(RecognitionJob).count()
            
            return {
                "jobs": [
                    {
                        "job_id": job.job_id,
                        "assertion_id": job.assertion_id,
                        "total_entities": job.total_entities,
                        "avg_confidence": job.avg_confidence,
                        "language": job.language,
                        "created_at": job.created_at.isoformat()
                    }
                    for job in jobs
                ],
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.get("/api/assertions/{assertion_id}/entities")
async def get_entities_by_assertion(assertion_id: str):
    """
    Get all entities for a specific assertion.
    
    Args:
        assertion_id: Assertion ID
    
    Returns:
        Entities for the assertion
    """
    try:
        with db.get_session() as session:
            jobs = session.query(RecognitionJob)\
                .filter(RecognitionJob.assertion_id == assertion_id)\
                .order_by(RecognitionJob.created_at.desc())\
                .all()
            
            if not jobs:
                raise HTTPException(status_code=404, detail=f"No entities found for assertion {assertion_id}")
            
            # Return the most recent job's entities
            latest_job = jobs[0]
            
            return {
                "assertion_id": assertion_id,
                "job_id": latest_job.job_id,
                "entities": json.loads(latest_job.output_entities),
                "total_entities": latest_job.total_entities,
                "avg_confidence": latest_job.avg_confidence,
                "created_at": latest_job.created_at.isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve entities: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Enhanced health check endpoint with component status."""
    health_checker = get_health_checker()
    
    # Check database health
    try:
        from sqlalchemy import text
        with db.get_session() as session:
            session.execute(text("SELECT 1"))
        
        health_checker.register_check(
            "database",
            "healthy",
            "Database connection OK",
            {"connection": "active"}
        )
    except Exception as e:
        health_checker.register_check(
            "database",
            "unhealthy",
            f"Database check failed: {str(e)}"
        )
    
    # Check CLASSLA NER availability
    try:
        from modules.entity_recognizer.service import _get_classla_pipeline
        pipeline = _get_classla_pipeline()
        if pipeline:
            health_checker.register_check(
                "classla_ner",
                "healthy",
                "CLASSLA NER available",
                {"model": "sr"}
            )
        else:
            health_checker.register_check(
                "classla_ner",
                "degraded",
                "CLASSLA NER not available, using regex fallback"
            )
    except Exception as e:
        health_checker.register_check(
            "classla_ner",
            "degraded",
            f"CLASSLA NER check failed: {str(e)}"
        )
    
    # Get overall health status
    health_status = health_checker.get_status()
    
    return {
        "module": "entity-recognizer",
        "version": "1.0.0",
        **health_status
    }


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get performance metrics."""
    try:
        metrics = get_metrics_collector()
        all_metrics = metrics.get_all_metrics()
        
        return {
            "status": "success",
            "metrics": all_metrics,
            "module": "entity-recognizer"
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
