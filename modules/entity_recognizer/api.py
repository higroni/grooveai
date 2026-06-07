"""
FastAPI endpoints for Entity Recognizer module.
"""

import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from modules.entity_recognizer.models import (
    RecognitionRequest,
    RecognitionResponse,
    RecognitionJob,
    EntityDB
)
from modules.entity_recognizer import service
from modules.entity_recognizer.database import db

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
        raise HTTPException(status_code=500, detail=f"Entity recognition failed: {str(e)}")


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
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "module": "entity-recognizer",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Made with Bob
