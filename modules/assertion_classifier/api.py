"""
FastAPI endpoints for Assertion Classifier module.
"""

import time
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from modules.assertion_classifier.models import (
    ClassificationRequest,
    ClassificationResponse,
    Assertion,
    BatchClassificationRequest,
    BatchClassificationResponse,
    BatchClassificationResult
)
from modules.assertion_classifier.service import AssertionClassifierService
from modules.assertion_classifier.database import ClassificationDatabase
from shared.monitoring import (
    get_metrics_collector, get_health_checker
)


app = FastAPI(
    title="Assertion Classifier API",
    description="Classifies assertions into types: obligation, prohibition, permission, deadline, definition",
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
classifier_service = AssertionClassifierService()
db = ClassificationDatabase()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "module": "assertion-classifier",
        "version": "1.0.0",
        "status": "running",
        "description": "Classifies assertions into types",
        "types": ["obligation", "prohibition", "permission", "deadline", "definition"],
        "endpoints": {
            "/classify": "POST - Classify an assertion",
            "/classify/batch": "POST - Classify multiple assertions with detailed timing metrics",
            "/stats": "GET - Get classification statistics",
            "/patterns": "GET - Get available patterns",
            "/health": "GET - Health check"
        }
    }


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
        total = db.get_total_classifications()
        health_checker.register_check(
            "database", "healthy", f"Database connection OK ({total} classifications)"
        )
    except Exception as e:
        health_checker.register_check(
            "database", "unhealthy", f"Database check failed: {str(e)}"
        )
    
    health_status = health_checker.get_status()
    return {
        "module": "assertion-classifier",
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
            "module": "assertion-classifier"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify", response_model=ClassificationResponse)
async def classify_assertion(request: ClassificationRequest):
    """
    Classify a single assertion.
    
    Args:
        request: Classification request with assertion data
        
    Returns:
        Classification response with result and metadata
    """
    try:
        start_time = time.time()
        job_id = str(uuid.uuid4())
        
        # Classify assertion
        output = classifier_service.classify_assertion(
            assertion=request.assertion,
            language=request.language,
            min_confidence=request.min_confidence
        )
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Save to database
        db.save_classification(
            job_id=job_id,
            output=output,
            language=request.language,
            processing_time_ms=processing_time_ms
        )
        
        # Create response
        response = ClassificationResponse(
            module="assertion-classifier",
            status="success",
            job_id=job_id,
            output=output,
            metadata={
                "processing_time_ms": processing_time_ms,
                "language": request.language,
                "min_confidence": request.min_confidence
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify/batch", response_model=BatchClassificationResponse)
async def classify_batch(request: BatchClassificationRequest):
    """
    Classify multiple assertions in batch with detailed timing metrics.
    
    This endpoint processes multiple assertions efficiently, providing:
    - Per-assertion timing metrics
    - Graceful error handling (partial success supported)
    - Detailed performance statistics
    - Pattern matching statistics
    
    Args:
        request: Batch classification request with assertions and parameters
        
    Returns:
        Batch classification response with results and timing metrics
    """
    metrics = get_metrics_collector()
    batch_start = time.time()
    
    try:
        results = []
        successful = 0
        failed = 0
        per_assertion_times = []
        db_save_times = []
        
        # Process each assertion
        for assertion in request.assertions:
            assertion_start = time.time()
            
            try:
                # Classify assertion
                output = classifier_service.classify_assertion(
                    assertion=assertion,
                    language=request.language,
                    min_confidence=request.min_confidence
                )
                
                processing_time_ms = int((time.time() - assertion_start) * 1000)
                per_assertion_times.append(processing_time_ms)
                
                # Save to database
                db_start = time.time()
                job_id = str(uuid.uuid4())
                db.save_classification(
                    job_id=job_id,
                    output=output,
                    language=request.language,
                    processing_time_ms=processing_time_ms
                )
                db_save_times.append(int((time.time() - db_start) * 1000))
                
                # Create result
                result = BatchClassificationResult(
                    assertion_id=assertion.assertion_id,
                    status="success",
                    classification=output.classification,
                    error=None,
                    processing_time_ms=processing_time_ms
                )
                results.append(result)
                successful += 1
                
            except Exception as e:
                # Handle individual assertion failure
                processing_time_ms = int((time.time() - assertion_start) * 1000)
                per_assertion_times.append(processing_time_ms)
                
                result = BatchClassificationResult(
                    assertion_id=assertion.assertion_id,
                    status="error",
                    classification=None,
                    error=str(e),
                    processing_time_ms=processing_time_ms
                )
                results.append(result)
                failed += 1
        
        # Calculate timing metrics
        total_time_ms = int((time.time() - batch_start) * 1000)
        processing_time_ms = sum(per_assertion_times)
        db_save_time_ms = sum(db_save_times)
        
        # Determine overall status
        if failed == 0:
            status = "success"
        elif successful == 0:
            status = "error"
        else:
            status = "partial"
        
        # Calculate type distribution from successful results
        type_counts = {}
        for result in results:
            if result.status == "success" and result.classification:
                assertion_type = result.classification.assertion_type
                type_counts[assertion_type] = type_counts.get(assertion_type, 0) + 1
        
        # Record metrics
        metrics.record(
            "processing_duration_ms",
            total_time_ms,
            {"endpoint": "/batch", "status": status}
        )
        
        # Create response with detailed metadata
        response = BatchClassificationResponse(
            module="assertion-classifier",
            status=status,
            total_assertions=len(request.assertions),
            successful=successful,
            failed=failed,
            results=results,
            metadata={
                "timing": {
                    "total_ms": total_time_ms,
                    "processing_ms": processing_time_ms,
                    "db_save_ms": db_save_time_ms,
                    "per_assertion_ms": per_assertion_times,
                    "avg_time_per_assertion_ms": round(sum(per_assertion_times) / len(per_assertion_times), 2) if per_assertion_times else 0,
                    "throughput_assertions_per_sec": round(len(request.assertions) / (total_time_ms / 1000), 2) if total_time_ms > 0 else 0
                },
                "classification_stats": {
                    "type_distribution": type_counts,
                    "language": request.language,
                    "min_confidence": request.min_confidence
                }
            }
        )
        
        return response
        
    except Exception as e:
        # Record error metrics
        error_time = int((time.time() - batch_start) * 1000)
        metrics.record(
            "processing_duration_ms",
            error_time,
            {"endpoint": "/batch", "status": "error"}
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats(days: int = 7):
    """
    Get classification statistics.
    
    Args:
        days: Number of days to retrieve (default: 7)
        
    Returns:
        Statistics dictionary
    """
    try:
        stats = db.get_stats(days=days)
        distribution = db.get_type_distribution()
        
        return {
            "total_classifications": db.get_total_classifications(),
            "type_distribution": distribution,
            "recent_stats": [
                {
                    "date": s.date.isoformat(),
                    "total": s.total_classifications,
                    "obligation": s.obligation_count,
                    "prohibition": s.prohibition_count,
                    "permission": s.permission_count,
                    "deadline": s.deadline_count,
                    "definition": s.definition_count,
                    "avg_confidence": round(s.avg_confidence, 2)
                }
                for s in stats
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/patterns")
async def get_patterns(language: str = "sr"):
    """
    Get available classification patterns.
    
    Args:
        language: Language code (default: "sr")
        
    Returns:
        Pattern statistics
    """
    try:
        return classifier_service.get_pattern_stats(language=language)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/classification/{job_id}")
async def get_classification(job_id: str):
    """
    Get classification by job ID.
    
    Args:
        job_id: Job ID to retrieve
        
    Returns:
        Classification details
    """
    try:
        classification = db.get_classification(job_id)
        
        if classification is None:
            raise HTTPException(status_code=404, detail="Classification not found")
        
        return {
            "job_id": classification.job_id,
            "assertion_id": classification.assertion_id,
            "assertion_type": classification.assertion_type,
            "confidence": classification.confidence,
            "matched_patterns": classification.matched_patterns,
            "reasoning": classification.reasoning,
            "language": classification.language,
            "processing_time_ms": classification.processing_time_ms,
            "created_at": classification.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/classifications/type/{assertion_type}")
async def get_classifications_by_type(assertion_type: str, limit: int = 100):
    """
    Get classifications by type.
    
    Args:
        assertion_type: Type to filter by
        limit: Maximum number of results
        
    Returns:
        List of classifications
    """
    try:
        valid_types = ["obligation", "prohibition", "permission", "deadline", "definition"]
        if assertion_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid type. Must be one of: {', '.join(valid_types)}"
            )
        
        classifications = db.get_classifications_by_type(assertion_type, limit)
        
        return {
            "type": assertion_type,
            "count": len(classifications),
            "classifications": [
                {
                    "job_id": c.job_id,
                    "assertion_id": c.assertion_id,
                    "confidence": c.confidence,
                    "created_at": c.created_at.isoformat()
                }
                for c in classifications
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
