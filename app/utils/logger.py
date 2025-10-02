"""
Logging configuration and utilities for the Procurement RAG System
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import configuration
try:
    from config import LOG_LEVEL, LOG_FILE, LOGS_DIR
except ImportError:
    # Fallback configuration if config.py is not available
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/app.log"
    LOGS_DIR = Path("logs")

# ========================================
# LOGGING CONFIGURATION
# ========================================

def setup_logger(
    name: str = "procurement_rag",
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up a logger with file and console handlers
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        console_output: Whether to output to console
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level or LOG_LEVEL.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler (10MB max, keep 5 files)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = "procurement_rag") -> logging.Logger:
    """
    Get or create a logger instance
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return setup_logger(name)

# ========================================
# SPECIALIZED LOGGERS
# ========================================

def get_api_logger() -> logging.Logger:
    """Get logger for API operations"""
    return get_logger("procurement_rag.api")

def get_rag_logger() -> logging.Logger:
    """Get logger for RAG operations"""
    return get_logger("procurement_rag.rag")

def get_ui_logger() -> logging.Logger:
    """Get logger for UI operations"""
    return get_logger("procurement_rag.ui")

def get_system_logger() -> logging.Logger:
    """Get logger for system operations"""
    return get_logger("procurement_rag.system")

# ========================================
# LOGGING UTILITIES
# ========================================

class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(f"procurement_rag.{self.__class__.__name__}")

def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise
    return wrapper

def log_execution_time(func):
    """Decorator to log function execution time"""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        start_time = datetime.now()
        logger.debug(f"Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} completed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {e}")
            raise
    return wrapper

# ========================================
# LOG ANALYSIS UTILITIES
# ========================================

def analyze_logs(log_file: str = None) -> dict:
    """
    Analyze log file for patterns and statistics
    
    Args:
        log_file: Path to log file
    
    Returns:
        Dictionary with log analysis
    """
    if not log_file:
        log_file = LOG_FILE
    
    if not os.path.exists(log_file):
        return {"error": "Log file not found"}
    
    analysis = {
        "total_lines": 0,
        "error_count": 0,
        "warning_count": 0,
        "info_count": 0,
        "debug_count": 0,
        "recent_errors": [],
        "most_common_errors": {}
    }
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                analysis["total_lines"] += 1
                
                if "ERROR" in line:
                    analysis["error_count"] += 1
                    analysis["recent_errors"].append(line.strip())
                elif "WARNING" in line:
                    analysis["warning_count"] += 1
                elif "INFO" in line:
                    analysis["info_count"] += 1
                elif "DEBUG" in line:
                    analysis["debug_count"] += 1
        
        # Keep only last 10 errors
        analysis["recent_errors"] = analysis["recent_errors"][-10:]
        
    except Exception as e:
        analysis["error"] = f"Failed to analyze logs: {e}"
    
    return analysis

def clear_old_logs(days: int = 7):
    """
    Clear log files older than specified days
    
    Args:
        days: Number of days to keep logs
    """
    logger = get_system_logger()
    logs_dir = Path(LOGS_DIR)
    
    if not logs_dir.exists():
        return
    
    cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
    deleted_count = 0
    
    for log_file in logs_dir.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_date:
            try:
                log_file.unlink()
                deleted_count += 1
                logger.info(f"Deleted old log file: {log_file}")
            except Exception as e:
                logger.error(f"Failed to delete {log_file}: {e}")
    
    logger.info(f"Cleaned up {deleted_count} old log files")

# ========================================
# INITIALIZATION
# ========================================

# Set up default logger
default_logger = setup_logger()

# Log system startup
default_logger.info("Logging system initialized")
default_logger.info(f"Log level: {LOG_LEVEL}")
default_logger.info(f"Log file: {LOG_FILE}")

# Ensure logs directory exists
Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
