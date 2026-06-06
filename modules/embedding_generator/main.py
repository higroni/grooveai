"""
Main entry point for Embedding Generator module.

Starts the FastAPI server for embedding generation.
"""

from modules.embedding_generator.api import app, logger
from shared.config_loader import config
import uvicorn


def main():
    """Start the Embedding Generator API server."""
    port = config.get_module_port("embedding_generator")
    host = config.get_module_host("embedding_generator")
    
    logger.info(f"Starting Embedding Generator module on {host}:{port}")
    logger.info(f"Model: {config.get_embedding_model()}")
    logger.info(f"Embedding dimension: {config.get_embedding_dimensions()}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=config.get_log_level().lower()
    )


if __name__ == "__main__":
    main()

# Made with Bob
