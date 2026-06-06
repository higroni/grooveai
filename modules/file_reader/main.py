"""
Main entry point for File Reader module
Run with: python -m modules.file_reader.main
"""
import uvicorn
from shared.config_loader import config
from modules.file_reader.api import app, logger


def main():
    """Start the File Reader module"""
    port = config.get_module_port("file_reader")
    host = config.get("network.modules.file_reader.host", "0.0.0.0")
    
    logger.info(f"Starting File Reader module on {host}:{port}")
    logger.info(f"Sample file: {config.get_sample_file()}")
    
    uvicorn.run(
        "modules.file_reader.api:app",
        host=host,
        port=port,
        reload=config.get("development.auto_reload", False),
        log_level=config.get("global.log_level", "info").lower()
    )


if __name__ == "__main__":
    main()

# Made with Bob
