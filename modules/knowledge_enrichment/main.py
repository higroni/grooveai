"""
Knowledge Enrichment Module - Main Entry Point
Runs the FastAPI server on port 8110
"""

import uvicorn
import logging
import yaml
from pathlib import Path

from .api import create_app
from .service import KnowledgeEnrichmentService


def setup_logging(log_file: str, log_level: str = "INFO"):
    """Setup logging configuration"""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def main():
    """Main entry point"""
    # Load configuration
    config = load_config()
    
    # Setup logging
    log_config = config.get('logging', {})
    log_file = log_config.get('knowledge_enrichment', 'data/logs/knowledge_enrichment.log')
    log_level = log_config.get('level', 'INFO')
    setup_logging(log_file, log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Knowledge Enrichment Module...")
    
    # Initialize service (uses unified database)
    service = KnowledgeEnrichmentService()
    logger.info("Initialized service with unified database")
    
    # Create FastAPI app
    app = create_app(service)
    
    # Get network configuration
    network_config = config.get('network', {}).get('knowledge_enrichment', {})
    host = network_config.get('host', '0.0.0.0')
    port = network_config.get('port', 8110)
    
    # Run server
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

# Made with Bob
