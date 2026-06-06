"""
Latinizer Module Entry Point.

Starts the FastAPI server for Cyrillic-to-Latin text conversion.
"""

import uvicorn
from shared.config_loader import config
from shared.logger import get_module_logger

# Initialize logger
logger = get_module_logger("latinizer", config.get_log_level())


def main():
    """Start the Latinizer API server."""
    port = config.get_module_port("latinizer")
    host = "0.0.0.0"
    
    logger.info(f"Starting Latinizer module on {host}:{port}")
    
    try:
        uvicorn.run(
            "modules.latinizer.api:app",
            host=host,
            port=port,
            log_level=config.get_log_level().lower()
        )
    except Exception as e:
        logger.error(f"Failed to start Latinizer module: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

# Made with Bob
