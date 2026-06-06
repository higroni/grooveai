"""
Main entry point for Text Normalizer module
Run with: python -m modules.text_normalizer.main
"""
import uvicorn
from shared.config_loader import config
from modules.text_normalizer.api import app, logger


def main():
    """Start the Text Normalizer module"""
    port = config.get_module_port("text_normalizer")
    host = config.get("network.modules.text_normalizer.host", "0.0.0.0")
    
    logger.info(f"Starting Text Normalizer module on {host}:{port}")
    
    uvicorn.run(
        "modules.text_normalizer.api:app",
        host=host,
        port=port,
        reload=config.get("development.auto_reload", False),
        log_level=config.get("global.log_level", "info").lower()
    )


if __name__ == "__main__":
    main()

# Made with Bob
