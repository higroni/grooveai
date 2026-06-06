"""
FastAPI application for File Reader module
Port: 8101
"""
import uuid
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from modules.file_reader.service import FileReaderService
from modules.file_reader.database import db
from modules.file_reader.models import FileReaderJob
from shared.config_loader import config


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.get("global.log_level", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("file_reader")


# Pydantic models for API
class ReadRequest(BaseModel):
    """Request model for reading a file"""
    file_path: str = Field(..., description="Path to the file to read")
    file_type: Optional[str] = Field(None, description="File type (pdf, docx, txt). Auto-detected if not provided")


class ReadResponse(BaseModel):
    """Response model for file reading"""
    module: str = "file-reader"
    status: str
    job_id: str
    output: Optional[dict] = None
    metadata: Optional[dict] = None
    error: Optional[str] = None


class JobResponse(BaseModel):
    """Response model for job details"""
    job_id: str
    file_path: str
    file_type: str
    status: str
    output_text: Optional[str] = None
    char_count: Optional[int] = None
    page_count: Optional[int] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


# Initialize FastAPI app
app = FastAPI(
    title="File Reader Module",
    description="Reads PDF, DOCX, and TXT files and extracts raw text",
    version="1.0.0"
)

# Initialize service
file_reader_service = FileReaderService()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "module": "file-reader",
        "version": "1.0.0",
        "status": "running",
        "port": config.get_module_port("file_reader")
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "module": "file-reader"
    }


@app.post("/api/read", response_model=ReadResponse)
async def read_file(request: ReadRequest):
    """
    Read a file and extract text
    
    Args:
        request: ReadRequest with file_path and optional file_type
        
    Returns:
        ReadResponse with extracted text and metadata
    """
    job_id = str(uuid.uuid4())
    
    logger.info(f"[{job_id}] Starting file read: {request.file_path}")
    
    # Create job record
    job = FileReaderJob(
        job_id=job_id,
        file_path=request.file_path,
        file_type=request.file_type or "auto",
        status="processing"
    )
    
    try:
        with db.get_session() as session:
            session.add(job)
            session.commit()
        
        # Read file
        result = file_reader_service.read_file(request.file_path, request.file_type)
        
        # Update job with results
        with db.get_session() as session:
            job = session.query(FileReaderJob).filter_by(job_id=job_id).first()
            if job:
                job.status = "success"
                job.output_text = result["text"]
                job.char_count = result["char_count"]
                job.page_count = result["page_count"]
                job.processing_time_ms = result["processing_time_ms"]
                job.completed_at = datetime.utcnow()
                session.commit()
        
        logger.info(f"[{job_id}] File read successful: {result['char_count']} chars, {result['page_count']} pages")
        
        return ReadResponse(
            status="success",
            job_id=job_id,
            output={
                "text": result["text"],
                "encoding": result["encoding"],
                "char_count": result["char_count"],
                "page_count": result["page_count"]
            },
            metadata={
                "processing_time_ms": result["processing_time_ms"],
                "file_path": request.file_path
            }
        )
        
    except FileNotFoundError as e:
        logger.error(f"[{job_id}] File not found: {str(e)}")
        
        with db.get_session() as session:
            job = session.query(FileReaderJob).filter_by(job_id=job_id).first()
            if job:
                job.status = "error"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                session.commit()
        
        raise HTTPException(status_code=404, detail=str(e))
        
    except ValueError as e:
        logger.error(f"[{job_id}] Invalid input: {str(e)}")
        
        with db.get_session() as session:
            job = session.query(FileReaderJob).filter_by(job_id=job_id).first()
            if job:
                job.status = "error"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                session.commit()
        
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"[{job_id}] Error reading file: {str(e)}")
        
        with db.get_session() as session:
            job = session.query(FileReaderJob).filter_by(job_id=job_id).first()
            if job:
                job.status = "error"
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                session.commit()
        
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """
    Get job details by ID
    
    Args:
        job_id: Job ID
        
    Returns:
        JobResponse with job details
    """
    with db.get_session() as session:
        job = session.query(FileReaderJob).filter_by(job_id=job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        return JobResponse(**job.to_dict())


@app.get("/api/jobs", response_model=List[JobResponse])
async def list_jobs(limit: int = 100, offset: int = 0):
    """
    List all jobs
    
    Args:
        limit: Maximum number of jobs to return
        offset: Number of jobs to skip
        
    Returns:
        List of JobResponse
    """
    with db.get_session() as session:
        jobs = session.query(FileReaderJob)\
            .order_by(FileReaderJob.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return [JobResponse(**job.to_dict()) for job in jobs]


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job
    
    Args:
        job_id: Job ID
        
    Returns:
        Success message
    """
    with db.get_session() as session:
        job = session.query(FileReaderJob).filter_by(job_id=job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        session.delete(job)
        session.commit()
        
        logger.info(f"Deleted job: {job_id}")
        
        return {"status": "success", "message": f"Job {job_id} deleted"}


if __name__ == "__main__":
    import uvicorn
    
    port = config.get_module_port("file_reader")
    host = config.get("network.modules.file_reader.host", "0.0.0.0")
    
    logger.info(f"Starting File Reader module on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=config.get("global.log_level", "info").lower()
    )

# Made with Bob
