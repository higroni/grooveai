"""
Entity Recognizer Module - Main Entry Point

Recognizes named entities in legal assertions including:
- PERSON, ORGANIZATION, DATE, MONEY, LEGAL_REF, LOCATION, PERCENTAGE, DURATION
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from fastapi import FastAPI
from shared.logger import ModuleLogger
from shared.config_loader import config
from modules.entity_recognizer.api import router
from modules.entity_recognizer.database import db

# Initialize logger
logger = ModuleLogger("entity-recognizer")

# Create FastAPI app
app = FastAPI(
    title="Entity Recognizer Module",
    description="Recognizes named entities in legal assertions",
    version="1.0.0"
)

# Include router
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Entity Recognizer module started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Entity Recognizer module shutting down")


if __name__ == "__main__":
    port = config.get_module_port("entity_recognizer")
    logger.info(f"Starting Entity Recognizer module on port {port}")
    logger.info("Supported entity types: PERSON, ORGANIZATION, DATE, MONEY, LEGAL_REF, LOCATION, PERCENTAGE, DURATION")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

# Made with Bob
