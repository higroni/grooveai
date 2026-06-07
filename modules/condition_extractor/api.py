"""
FastAPI application for Condition Extractor module.
"""
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    ConditionExtractionRequest,
    ConditionExtractionResponse,
    HealthResponse,
    BatchConditionExtractionRequest,
    BatchConditionExtractionResponse,
    BatchConditionExtractionResult
)
from .service import ConditionExtractorService
from .database import ConditionExtractorDatabase
from shared.monitoring import (
    get_metrics_collector, get_health_checker
)


def create_app(database_url: str) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Args:
        database_url: Database connection URL
        
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Condition Extractor API",
        description="Extract conditions, exceptions, temporal and modal clauses from legal assertions",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize service and database
    service = ConditionExtractorService()
    database = ConditionExtractorDatabase()
    
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """
        Enhanced health check endpoint with component status.
        
        Returns:
            Health status with database component check
        """
        health_checker = get_health_checker()
        
        # Check database connection
        try:
            from sqlalchemy import text
            with database.get_session() as session:
                session.execute(text("SELECT 1"))
            health_checker.register_check(
                "database", "healthy", "Database connection OK"
            )
        except Exception as e:
            health_checker.register_check(
                "database", "unhealthy", f"Database check failed: {str(e)}"
            )
        
        health_status = health_checker.get_status()
        return {
            "module": "condition_extractor",
            "version": "1.0.0",
            **health_status
        }
    
    @app.get("/metrics")
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
                "module": "condition_extractor"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/extract", response_model=ConditionExtractionResponse)
    async def extract_conditions(request: ConditionExtractionRequest):
        """
        Extract conditions from an assertion.
        
        Args:
            request: Condition extraction request
            
        Returns:
            Extraction response with conditions
        """
        try:
            # Generate job ID
            job_id = str(uuid.uuid4())
            
            # Extract conditions
            output = service.extract_conditions(request)
            
            # Save to database
            database.save_extraction_job(
                job_id=job_id,
                assertion_id=request.assertion.assertion_id,
                assertion_text=request.assertion.text,
                output=output
            )
            
            # Create response
            response = ConditionExtractionResponse(
                job_id=job_id,
                assertion_id=request.assertion.assertion_id,
                output=output,
                status="completed"
            )
            
            return response
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/extract/batch", response_model=BatchConditionExtractionResponse)
    async def extract_conditions_batch(request: BatchConditionExtractionRequest):
        """
        Extract conditions from multiple assertions in batch.
        
        This endpoint processes multiple assertions efficiently by:
        - Processing assertions in batches to optimize memory usage
        - Tracking detailed timing metrics for performance analysis
        - Handling errors gracefully per assertion
        
        Args:
            request: BatchConditionExtractionRequest with list of assertions
            
        Returns:
            BatchConditionExtractionResponse with results for each assertion and detailed timing
        """
        import time
        import logging
        
        logger = logging.getLogger(__name__)
        metrics = get_metrics_collector()
        batch_start = time.time()
        
        try:
            logger.info(f"Starting batch condition extraction for {len(request.assertions)} assertions")
            
            # Generate batch job ID
            job_id = str(uuid.uuid4())
            
            # Timing metrics
            timings = {
                "total_ms": 0,
                "processing_ms": 0,
                "db_save_ms": 0,
                "per_assertion_ms": []
            }
            
            results = []
            successful = 0
            failed = 0
            
            # Process each assertion
            processing_start = time.time()
            for assertion in request.assertions:
                assertion_start = time.time()
                
                try:
                    # Create individual request
                    from .models import ConditionExtractionRequest as SingleRequest
                    single_request = SingleRequest(
                        assertion=assertion,
                        language=request.language,
                        min_confidence=request.min_confidence,
                        extract_conditions=request.extract_conditions,
                        extract_exceptions=request.extract_exceptions,
                        extract_temporal=request.extract_temporal,
                        extract_modal=request.extract_modal
                    )
                    
                    # Extract conditions for this assertion
                    output = service.extract_conditions(single_request)
                    
                    assertion_time_ms = (time.time() - assertion_start) * 1000
                    timings["per_assertion_ms"].append({
                        "assertion_id": assertion.assertion_id,
                        "time_ms": assertion_time_ms,
                        "conditions_found": output.total_conditions
                    })
                    
                    results.append(BatchConditionExtractionResult(
                        assertion_id=assertion.assertion_id,
                        status="success",
                        output=output,
                        error=None,
                        processing_time_ms=assertion_time_ms
                    ))
                    
                    successful += 1
                    logger.debug(f"Processed assertion {assertion.assertion_id} in {assertion_time_ms:.2f}ms ({output.total_conditions} conditions)")
                    
                except Exception as e:
                    assertion_time_ms = (time.time() - assertion_start) * 1000
                    timings["per_assertion_ms"].append({
                        "assertion_id": assertion.assertion_id,
                        "time_ms": assertion_time_ms,
                        "error": str(e)
                    })
                    
                    results.append(BatchConditionExtractionResult(
                        assertion_id=assertion.assertion_id,
                        status="error",
                        output=None,
                        error=str(e),
                        processing_time_ms=assertion_time_ms
                    ))
                    
                    failed += 1
                    logger.error(f"Error processing assertion {assertion.assertion_id}: {str(e)}")
            
            timings["processing_ms"] = (time.time() - processing_start) * 1000
            
            # Save batch results to database
            db_start = time.time()
            for result in results:
                if result.status == "success" and result.output:
                    database.save_extraction_job(
                        job_id=f"{job_id}_{result.assertion_id}",
                        assertion_id=result.assertion_id,
                        assertion_text=next(a.text for a in request.assertions if a.assertion_id == result.assertion_id),
                        output=result.output
                    )
            
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
            total_conditions = sum(r.output.total_conditions for r in results if r.output)
            
            # Record metrics
            metrics.record(
                "processing_duration_ms",
                timings["total_ms"],
                {"endpoint": "/batch", "status": status}
            )
            
            logger.info(
                f"Batch extraction complete: {successful} successful, {failed} failed, "
                f"{timings['total_ms']:.2f}ms total, {avg_time_per_assertion:.2f}ms avg per assertion"
            )
            
            return BatchConditionExtractionResponse(
                module="condition-extractor",
                status=status,
                job_id=job_id,
                results=results,
                metadata={
                    "total_assertions": len(request.assertions),
                    "successful": successful,
                    "failed": failed,
                    "total_conditions": total_conditions,
                    "timings": timings,
                    "avg_time_per_assertion_ms": avg_time_per_assertion,
                    "throughput_assertions_per_sec": len(request.assertions) / (timings["total_ms"] / 1000) if timings["total_ms"] > 0 else 0
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
            
            logger.error(f"Error in batch condition extraction: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Batch condition extraction failed: {str(e)}")
    
    @app.get("/api/jobs/{job_id}", response_model=ConditionExtractionResponse)
    async def get_job(job_id: str):
        """
        Get extraction job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job details
        """
        try:
            job = database.get_job(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            
            # Parse output conditions
            import json
            conditions_data = json.loads(job.output_conditions)
            from .models import ExtractedCondition, ConditionExtractionOutput
            
            conditions = [ExtractedCondition(**c) for c in conditions_data]
            
            output = ConditionExtractionOutput(
                conditions=conditions,
                total_conditions=job.total_conditions,
                total_exceptions=job.total_exceptions,
                total_temporal=job.total_temporal,
                total_modal=job.total_modal,
                average_confidence=job.average_confidence,
                processing_time_ms=job.processing_time_ms
            )
            
            response = ConditionExtractionResponse(
                job_id=job.job_id,
                assertion_id=job.assertion_id,
                output=output,
                status="completed",
                created_at=job.created_at
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/assertions/{assertion_id}/conditions")
    async def get_conditions_by_assertion(assertion_id: str):
        """
        Get all conditions for an assertion.
        
        Args:
            assertion_id: Assertion identifier
            
        Returns:
            List of conditions
        """
        try:
            conditions = database.get_conditions_by_assertion(assertion_id)
            
            return {
                "assertion_id": assertion_id,
                "total_conditions": len(conditions),
                "conditions": [c.dict() for c in conditions]
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

# Made with Bob
