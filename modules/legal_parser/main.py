"""
Legal Parser Module - Entry Point

Starts the FastAPI server on port 8104.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import uvicorn
from shared.config_loader import config
from shared.logger import ModuleLogger

# Initialize logger
logger = ModuleLogger("legal-parser")

if __name__ == "__main__":
    port = config.get_module_port("legal_parser")
    logger.info(f"Starting Legal Parser module on port {port}")
    
    uvicorn.run(
        "modules.legal_parser.api:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

# Made with Bob
