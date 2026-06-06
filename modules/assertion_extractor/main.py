"""
Main entry point for Assertion Extractor module.
"""

import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.config_loader import config
from shared.logger import ModuleLogger
from modules.assertion_extractor.api import router

# Initialize logger
logger = ModuleLogger("assertion-extractor")

# Create FastAPI app
app = FastAPI(
    title="Assertion Extractor Module",
    description="Extracts legal assertions from legal units",
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

# Include router
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Starting Assertion Extractor module on port 8106")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down Assertion Extractor module")


if __name__ == "__main__":
    # Get port from config
    port = config.get_module_port("assertion_extractor")
    
    logger.info(f"Starting Assertion Extractor module on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

# Made with Bob
