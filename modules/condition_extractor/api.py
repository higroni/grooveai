"""
FastAPI application for Condition Extractor module.
"""
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    ConditionExtractionRequest,
    ConditionExtractionResponse,
    HealthResponse
)
from .service import ConditionExtractorService
from .database import ConditionExtractorDatabase


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
    database = ConditionExtractorDatabase(database_url)
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            module="condition_extractor",
            version="1.0.0"
        )
    
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
