"""
Shared logging utility for all GROOVE.AI modules.

This module provides a standardized logging configuration that:
- Creates module-specific log files
- Formats logs consistently across all modules
- Supports different log levels per module
- Handles Windows encoding issues (no emojis)
- Provides both file and console logging
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ModuleLogger:
    """
    Standardized logger for GROOVE.AI modules.
    
    Features:
    - Module-specific log files in data/logs/
    - Consistent formatting across all modules
    - Console and file handlers
    - Windows-safe (no emojis, proper encoding)
    """
    
    def __init__(
        self,
        module_name: str,
        log_level: str = "INFO",
        log_dir: str = "data/logs"
    ):
        """
        Initialize module logger.
        
        Args:
            module_name: Name of the module (e.g., "file_reader")
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files (relative to project root)
        """
        self.module_name = module_name
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = Path(log_dir)
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(module_name)
        self.logger.setLevel(self.log_level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatters
        self.file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.console_formatter = logging.Formatter(
            fmt='[%(levelname)s] %(name)s: %(message)s'
        )
        
        # Add handlers
        self._add_file_handler()
        self._add_console_handler()
    
    def _add_file_handler(self):
        """Add file handler for persistent logging."""
        # Create log filename with date
        log_filename = f"{self.module_name}_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = self.log_dir / log_filename
        
        # Create file handler
        file_handler = logging.FileHandler(
            log_path,
            mode='a',
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.file_formatter)
        
        self.logger.addHandler(file_handler)
    
    def _add_console_handler(self):
        """Add console handler for real-time logging (unless in batch mode)."""
        # Skip console logging if in batch processing mode
        if os.environ.get('GROOVE_BATCH_MODE') == '1':
            return
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(self.console_formatter)
        
        self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.
        
        Returns:
            logging.Logger: Configured logger
        """
        return self.logger
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """
        Log error message.
        
        Args:
            message: Error message
            exc_info: Include exception traceback
        """
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """
        Log critical message.
        
        Args:
            message: Critical message
            exc_info: Include exception traceback
        """
        self.logger.critical(message, exc_info=exc_info)


def get_module_logger(
    module_name: str,
    log_level: Optional[str] = None,
    log_dir: Optional[str] = None
) -> ModuleLogger:
    """
    Factory function to create a module logger.
    
    Args:
        module_name: Name of the module
        log_level: Optional log level (defaults to INFO)
        log_dir: Optional log directory (defaults to data/logs)
    
    Returns:
        ModuleLogger: Configured logger instance
    
    Example:
        >>> logger = get_module_logger("file_reader", "DEBUG")
        >>> logger.info("Module started")
        >>> logger.error("Error occurred", exc_info=True)
    """
    kwargs = {"module_name": module_name}
    
    if log_level:
        kwargs["log_level"] = log_level
    
    if log_dir:
        kwargs["log_dir"] = log_dir
    
    return ModuleLogger(**kwargs)


# Example usage
if __name__ == "__main__":
    # Create logger for testing
    logger = get_module_logger("test_module", "DEBUG")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    print(f"\nLog file created in: data/logs/test_module_{datetime.now().strftime('%Y%m%d')}.log")

# Made with Bob
