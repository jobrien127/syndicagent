import logging
import sys
from datetime import datetime
from typing import Optional

def setup_logger(
    name: str = "agworld_reporter",
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up and configure logger"""
    
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = "agworld_reporter") -> logging.Logger:
    """Get existing logger or create new one"""
    return logging.getLogger(name) or setup_logger(name)

# Create default logger instance
logger = setup_logger()

class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
    
    def log_info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)
