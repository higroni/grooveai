"""
Knowledge Enrichment Module - API Layer
FastAPI endpoints for knowledge enrichment operations
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging
import time
from typing import Dict, Any

from .models import (
    EnrichmentRequest, EnrichmentResponse,
    BatchEnrichmentRequest, BatchEnrichmentResponse, BatchEnrichmentResult,
    OntologyMatchRequest, OntologyMatchResponse,
    ReferenceResolutionRequest, ReferenceResolutionResponse,
    DefinitionExtractionRequest, DefinitionExtractionResponse
)
from .service import KnowledgeEnrichmentService
from shared.monitoring import (
    get_metrics_collector, get_health_checker,
    record_request_metrics, check_database_health
)


def create_app(service: KnowledgeEnrichmentService) -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="Knowledge Enrichment Module",
        description="Enriches legal assertions with ontology, references, and definitions",
        version="1.0.0"
    )
    
    logger = logging.getLogger(__name__)
    
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """Enhanced health check endpoint with component status"""
        health_checker = get_health_checker()
        
        # Check database health
        try:
            # Test database connection with a simple query
            from sqlalchemy import text
            with service.db.get_session() as session:
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
        
        # Check cache health
        try:
            cache_stats = service.ontology_matcher.cache.get_stats()
            health_checker.register_check(
                "cache",
                "healthy",
                "Cache operational",
                {"size": cache_stats.get("size", 0)}
            )
        except Exception as e:
            health_checker.register_check(
                "cache",
                "degraded",
                f"Cache check failed: {str(e)}"
            )
        
        # Get overall health status
        health_status = health_checker.get_status()
        
        return {
            "module": "knowledge_enrichment",
            "version": "1.0.0",
            **health_status
        }
    
    @app.get("/cache/stats")
    async def get_cache_stats() -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_stats = service.ontology_matcher.cache.get_stats()
            return {
                "status": "success",
                "cache_stats": cache_stats
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/cache/clear")
    async def clear_cache() -> Dict[str, Any]:
        """Clear all cache entries"""
        try:
            # Get size before clearing
            stats_before = service.ontology_matcher.cache.get_stats()
            entries_cleared = stats_before.get("size", 0)
            
            service.ontology_matcher.cache.clear()
            
            return {
                "status": "success",
                "message": "Cache cleared successfully",
                "entries_cleared": entries_cleared
            }
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/metrics")
    async def get_metrics() -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            metrics = get_metrics_collector()
            all_metrics = metrics.get_all_metrics()
            
            return {
                "status": "success",
                "metrics": all_metrics,
                "module": "knowledge_enrichment"
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
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
        Enrich multiple assertions in batch with detailed timing metrics.
        
        This endpoint processes multiple assertions efficiently, providing:
        - Per-assertion timing metrics
        - Graceful error handling (partial success supported)
        - Detailed performance statistics
        - Ontology matching, reference resolution, and definition extraction
        
        Args:
            request: Batch enrichment request with assertions
            
        Returns:
            Batch enrichment response with results and timing metrics
        """
        try:
            logger.info(f"Batch enriching {len(request.assertions)} assertions")
            
            batch_start = time.time()
            results = []
            successful = 0
            failed = 0
            per_assertion_times = []
            
            # Get metrics collector
            metrics = get_metrics_collector()
            
            # Process each assertion
            for assertion_request in request.assertions:
                assertion_start = time.time()
                
                try:
                    # Enrich assertion
                    response = service.enrich_assertion(assertion_request)
                    processing_time_ms = (time.time() - assertion_start) * 1000
                    per_assertion_times.append(processing_time_ms)
                    
                    # Record metrics
                    metrics.record("enrichment_duration_ms", processing_time_ms,
                                 {"endpoint": "/enrich/batch", "status": "success"})
                    
                    # Create result
                    result = BatchEnrichmentResult(
                        assertion_id=assertion_request.assertion_id,
                        status="success" if response.success else "error",
                        enriched_assertion=response.enriched_assertion,
                        error=response.error,
                        processing_time_ms=processing_time_ms
                    )
                    results.append(result)
                    
                    if response.success:
                        successful += 1
                    else:
                        failed += 1
                        
                except Exception as e:
                    # Handle individual assertion failure
                    processing_time_ms = (time.time() - assertion_start) * 1000
                    per_assertion_times.append(processing_time_ms)
                    
                    result = BatchEnrichmentResult(
                        assertion_id=assertion_request.assertion_id,
                        status="error",
                        enriched_assertion=None,
                        error=str(e),
                        processing_time_ms=processing_time_ms
                    )
                    results.append(result)
                    failed += 1
                    
                    # Record error metrics
                    metrics.record("enrichment_duration_ms", processing_time_ms,
                                 {"endpoint": "/enrich/batch", "status": "error"})
            
            # Calculate timing metrics
            total_time_ms = (time.time() - batch_start) * 1000
            
            # Determine overall status
            if failed == 0:
                status = "success"
            elif successful == 0:
                status = "error"
            else:
                status = "partial"
            
            # Create response with detailed metadata
            response = BatchEnrichmentResponse(
                module="knowledge-enrichment",
                status=status,
                total_assertions=len(request.assertions),
                successful=successful,
                failed=failed,
                results=results,
                metadata={
                    "timing": {
                        "total_ms": round(total_time_ms, 2),
                        "per_assertion_ms": [round(t, 2) for t in per_assertion_times],
                        "avg_time_per_assertion_ms": round(sum(per_assertion_times) / len(per_assertion_times), 2) if per_assertion_times else 0,
                        "throughput_assertions_per_sec": round(len(request.assertions) / (total_time_ms / 1000), 2) if total_time_ms > 0 else 0
                    },
                    "enrichment_stats": {
                        "total_assertions": len(request.assertions),
                        "successful": successful,
                        "failed": failed
                    }
                }
            )
            
            return response
            
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
