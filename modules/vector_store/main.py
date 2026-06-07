"""
Main entry point for Vector Store module.

Starts the FastAPI server for vector storage and embedding generation.
"""

from modules.vector_store.api import app, logger
from shared.config_loader import config
import uvicorn


def main():
    """Start the Vector Store API server."""
    port = config.get_module_port("vector_store")
    host = config.get_module_host("vector_store")
    
    logger.info(f"Starting Vector Store module on {host}:{port}")
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

