"""
Knowledge Enrichment Module - API Layer
FastAPI endpoints for knowledge enrichment operations
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from .models import (
    EnrichmentRequest, EnrichmentResponse,
    BatchEnrichmentRequest, BatchEnrichmentResponse,
    OntologyMatchRequest, OntologyMatchResponse,
    ReferenceResolutionRequest, ReferenceResolutionResponse,
    DefinitionExtractionRequest, DefinitionExtractionResponse
)
from .service import KnowledgeEnrichmentService


def create_app(service: KnowledgeEnrichmentService) -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="Knowledge Enrichment Module",
        description="Enriches legal assertions with ontology, references, and definitions",
        version="1.0.0"
    )
    
    logger = logging.getLogger(__name__)
    
    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "module": "knowledge_enrichment",
            "version": "1.0.0"
        }
    
    @app.post("/enrich", response_model=EnrichmentResponse)
    async def enrich_assertion(request: EnrichmentRequest) -> EnrichmentResponse:
        """
        Enrich a single assertion with ontology, references, and definitions
        
        This endpoint:
        1. Matches entities against ontology (with auto-learning)
        2. Resolves legal references
        3. Extracts term definitions
        """
        try:
            logger.info(f"Enriching assertion {request.assertion_id}")
            response = service.enrich_assertion(request)
            return response
            
        except Exception as e:
            logger.error(f"Error enriching assertion: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/enrich/batch", response_model=BatchEnrichmentResponse)
    async def enrich_batch(request: BatchEnrichmentRequest) -> BatchEnrichmentResponse:
        """
        Enrich multiple assertions in batch
        """
        try:
            logger.info(f"Batch enriching {len(request.assertions)} assertions")
            
            results = []
            successful = 0
            failed = 0
            total_time = 0.0
            
            for assertion_request in request.assertions:
                response = service.enrich_assertion(assertion_request)
                results.append(response)
                total_time += response.processing_time_ms
                
                if response.success:
                    successful += 1
                else:
                    failed += 1
            
            return BatchEnrichmentResponse(
                success=True,
                results=results,
                total_processing_time_ms=total_time,
                successful_count=successful,
                failed_count=failed
            )
            
        except Exception as e:
            logger.error(f"Error in batch enrichment: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/ontology/match", response_model=OntologyMatchResponse)
    async def match_ontology(request: OntologyMatchRequest) -> OntologyMatchResponse:
        """
        Match text against ontology (standalone operation)
        
        This endpoint only performs ontology matching without
        reference resolution or definition extraction.
        """
        try:
            logger.info("Matching ontology terms")
            response = service.match_ontology(request)
            return response
            
        except Exception as e:
            logger.error(f"Error matching ontology: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/references/resolve", response_model=ReferenceResolutionResponse)
    async def resolve_references(request: ReferenceResolutionRequest) -> ReferenceResolutionResponse:
        """
        Resolve legal references (standalone operation)
        
        This endpoint only performs reference resolution without
        ontology matching or definition extraction.
        """
        try:
            logger.info("Resolving legal references")
            response = service.resolve_references(request)
            return response
            
        except Exception as e:
            logger.error(f"Error resolving references: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/definitions/extract", response_model=DefinitionExtractionResponse)
    async def extract_definitions(request: DefinitionExtractionRequest) -> DefinitionExtractionResponse:
        """
        Extract term definitions (standalone operation)
        
        This endpoint only performs definition extraction without
        ontology matching or reference resolution.
        """
        try:
            logger.info("Extracting definitions")
            response = service.extract_definitions(request)
            return response
            
        except Exception as e:
            logger.error(f"Error extracting definitions: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/stats")
    async def get_stats() -> Dict[str, Any]:
        """
        Get enrichment statistics
        
        Returns counts of:
        - Total ontology terms
        - Total relationships
        - Total references
        - Total definitions
        - Total enriched assertions
        - Average processing time
        """
        try:
            stats = service.get_stats()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/")
    async def root() -> Dict[str, Any]:
        """Root endpoint with module information"""
        return {
            "module": "knowledge_enrichment",
            "version": "1.0.0",
            "description": "Enriches legal assertions with ontology, references, and definitions",
            "endpoints": {
                "health": "/health",
                "enrich": "/enrich",
                "batch_enrich": "/enrich/batch",
                "ontology_match": "/ontology/match",
                "resolve_references": "/references/resolve",
                "extract_definitions": "/definitions/extract",
                "stats": "/stats"
            }
        }
    
    return app

# Made with Bob
