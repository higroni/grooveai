"""
Main entry point for Condition Extractor module.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from shared.config_loader import config
from .api import create_app


def main():
    """Main entry point."""
    # Get module configuration
    module_config = {
        "host": config.get_module_host("condition_extractor"),
        "port": config.get_module_port("condition_extractor")
    }
    db_config = config.get_database_url("condition_extractor")
    
    host = module_config["host"]
    port = module_config["port"]
    
    # Create database directory if it doesn't exist
    db_path = Path(db_config.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create FastAPI app
    app = create_app(db_config)
    
    # Run server
    print(f"Starting Condition Extractor on {host}:{port}")
    print(f"Database: {db_config}")
    print(f"API Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()

# Made with Bob
