#!/usr/bin/env python3
"""
Unified Logging Management Module
Provides structured logging with file and console output support
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored log formatter (console only)"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    # Log level emojis
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '📘',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }
    
    def format(self, record):
        # Add color
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
            record.msg = f"{self.EMOJIS.get(levelname, '')} {record.msg}"
        
        return super().format(record)


class CAFALogger:
    """CAFA Unified Logger"""
    
    def __init__(
        self,
        name: str = "CAFA",
        log_dir: str = "logs",
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True,
        file_output: bool = True,
    ):
        """
        Initialize logger
        
        Args:
            name: Logger name
            log_dir: Log file directory
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Maximum bytes per log file
            backup_count: Number of backup log files to keep
            console_output: Output to console
            file_output: Output to file
        """
        self.name = name
        self.log_dir = log_dir
        self.logger = logging.getLogger(name)
        
        # Set log level
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Clear existing handlers (avoid duplicates)
        self.logger.handlers.clear()
        
        # Create log directory
        if file_output:
            os.makedirs(log_dir, exist_ok=True)
        
        # Log formats
        console_format = '%(levelname)s [%(asctime)s] %(message)s'
        file_format = '%(levelname)s [%(asctime)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # Console handler (with colors)
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_formatter = ColoredFormatter(console_format, datefmt=date_format)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # File handler (rotating)
        if file_output:
            # Main log file
            log_file = os.path.join(log_dir, f"{name.lower()}.log")
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(file_format, datefmt=date_format)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            # Error log file (ERROR and above only)
            error_log_file = os.path.join(log_dir, f"{name.lower()}_error.log")
            error_handler = RotatingFileHandler(
                error_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            self.logger.addHandler(error_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """Log DEBUG level message"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log INFO level message"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log WARNING level message"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log ERROR level message"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log CRITICAL level message"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with stack trace"""
        self.logger.exception(message, *args, **kwargs)
    
    def log_request(self, method: str, endpoint: str, status_code: int, duration_ms: float):
        """Log HTTP request"""
        status_emoji = "✅" if 200 <= status_code < 300 else "❌"
        self.info(
            f"{status_emoji} {method} {endpoint} - {status_code} ({duration_ms:.2f}ms)"
        )
    
    def log_llm_call(self, provider: str, model: str, tokens: int, duration_s: float):
        """Log LLM call"""
        self.info(
            f"🤖 LLM call [{provider}/{model}] - {tokens} tokens ({duration_s:.2f}s)"
        )
    
    def log_memory_operation(self, operation: str, count: int, duration_ms: float):
        """Log memory operation"""
        self.info(
            f"🧠 Memory {operation} - {count} items ({duration_ms:.2f}ms)"
        )
    
    def get_logger(self):
        """Get underlying logger object"""
        return self.logger


# Global logger instance
_global_logger: Optional[CAFALogger] = None


def get_logger(
    name: str = "CAFA",
    log_level: str = "INFO",
    log_dir: str = "logs"
) -> CAFALogger:
    """
    Get global logger instance
    
    Args:
        name: Logger name
        log_level: Log level
        log_dir: Log directory
    
    Returns:
        CAFALogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = CAFALogger(
            name=name,
            log_level=log_level,
            log_dir=log_dir
        )
    return _global_logger


def setup_module_logger(module_name: str) -> CAFALogger:
    """
    Create independent logger for module
    
    Args:
        module_name: Module name
    
    Returns:
        CAFALogger instance
    """
    return CAFALogger(name=module_name)


# Usage example
if __name__ == "__main__":
    print("📝 Logging System Test")
    print("=" * 70)
    
    # Create logger
    logger = get_logger(name="CAFA_TEST", log_level="DEBUG")
    
    # Test log levels
    print("\n1️⃣ Test log levels:")
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    
    # Test specialized log methods
    print("\n2️⃣ Test specialized logging:")
    logger.log_request("POST", "/api/chat", 200, 245.67)
    logger.log_llm_call("openai", "gpt-3.5-turbo", 150, 1.23)
    logger.log_memory_operation("store", 5, 12.34)
    
    # Test exception logging
    print("\n3️⃣ Test exception logging:")
    try:
        1 / 0
    except Exception as e:
        logger.exception("Caught an exception")
    
    print("\n" + "=" * 70)
    print(f"✅ Logs saved to: logs/cafa_test.log")
