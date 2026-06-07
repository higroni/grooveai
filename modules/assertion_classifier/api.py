"""
FastAPI endpoints for Assertion Classifier module.
"""

import time
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from modules.assertion_classifier.models import (
    ClassificationRequest,
    ClassificationResponse,
    Assertion
)
from modules.assertion_classifier.service import AssertionClassifierService
from modules.assertion_classifier.database import ClassificationDatabase


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
            "/classify/batch": "POST - Classify multiple assertions",
            "/stats": "GET - Get classification statistics",
            "/patterns": "GET - Get available patterns",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "module": "assertion-classifier",
        "database": "connected",
        "total_classifications": db.get_total_classifications()
    }


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


@app.post("/classify/batch")
async def classify_batch(assertions: list[Assertion], language: str = "sr", min_confidence: float = 0.5):
    """
    Classify multiple assertions.
    
    Args:
        assertions: List of assertions to classify
        language: Language code (default: "sr")
        min_confidence: Minimum confidence threshold
        
    Returns:
        List of classification responses
    """
    try:
        start_time = time.time()
        
        # Classify all assertions
        outputs = classifier_service.classify_batch(
            assertions=assertions,
            language=language,
            min_confidence=min_confidence
        )
        
        # Save to database and create responses
        responses = []
        for output in outputs:
            job_id = str(uuid.uuid4())
            processing_time_ms = int((time.time() - start_time) * 1000 / len(assertions))
            
            db.save_classification(
                job_id=job_id,
                output=output,
                language=language,
                processing_time_ms=processing_time_ms
            )
            
            response = ClassificationResponse(
                module="assertion-classifier",
                status="success",
                job_id=job_id,
                output=output,
                metadata={
                    "processing_time_ms": processing_time_ms,
                    "language": language,
                    "min_confidence": min_confidence
                }
            )
            responses.append(response)
        
        return {
            "total": len(responses),
            "classifications": responses,
            "total_time_ms": int((time.time() - start_time) * 1000)
        }
        
    except Exception as e:
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
