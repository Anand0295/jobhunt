"""Centralized Logging Module.

This module provides a centralized logging system with support for multiple
handlers, formatters, log rotation, and structured logging. Designed for
production-ready applications with flexible configuration.
"""

import logging
import logging.handlers
import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime
import traceback


# Default log format
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DETAILED_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
JSON_FORMAT = 'json'


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging.
    
    Outputs log records as JSON objects for easy parsing and analysis.
    
    Example:
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(JSONFormatter())
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record to format.
        
        Returns:
            JSON string representation of the log record.
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data)


class LoggerManager:
    """Centralized logger manager for the application.
    
    Provides methods to configure and retrieve loggers with consistent
    formatting and handlers across the application.
    
    Attributes:
        log_dir (Path): Directory for log files.
        log_level (int): Default logging level.
        handlers (Dict): Dictionary of configured handlers.
    
    Example:
        >>> logger_mgr = LoggerManager(log_dir='logs', log_level='DEBUG')
        >>> logger = logger_mgr.get_logger('myapp')
        >>> logger.info('Application started')
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        log_dir: Union[str, Path] = 'logs',
        log_level: Union[str, int] = logging.INFO,
        format_style: str = 'default',
        enable_console: bool = True,
        enable_file: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5
    ):
        """Initialize the logger manager.
        
        Args:
            log_dir: Directory for log files.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            format_style: Log format style ('default', 'detailed', or 'json').
            enable_console: Enable console (stdout) logging.
            enable_file: Enable file logging with rotation.
            max_bytes: Maximum size of each log file before rotation.
            backup_count: Number of backup log files to keep.
        """
        # Prevent re-initialization in singleton
        if self._initialized:
            return
        
        self.log_dir = Path(log_dir)
        self.log_level = self._parse_log_level(log_level)
        self.format_style = format_style
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.handlers: Dict[str, logging.Handler] = {}
        self._loggers: Dict[str, logging.Logger] = {}
        
        # Create log directory if it doesn't exist
        if self.enable_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up root logger
        self._setup_root_logger()
        
        self._initialized = True
    
    def _parse_log_level(self, level: Union[str, int]) -> int:
        """Parse log level from string or int.
        
        Args:
            level: Log level as string or int.
        
        Returns:
            Integer log level.
        """
        if isinstance(level, int):
            return level
        
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        return level_map.get(level.upper(), logging.INFO)
    
    def _get_formatter(self) -> logging.Formatter:
        """Get formatter based on format style.
        
        Returns:
            Logging formatter instance.
        """
        if self.format_style == 'json':
            return JSONFormatter()
        elif self.format_style == 'detailed':
            return logging.Formatter(DETAILED_FORMAT)
        else:
            return logging.Formatter(DEFAULT_FORMAT)
    
    def _setup_root_logger(self) -> None:
        """Set up the root logger with configured handlers."""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Remove existing handlers to avoid duplicates
        root_logger.handlers.clear()
        
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(self._get_formatter())
            root_logger.addHandler(console_handler)
            self.handlers['console'] = console_handler
        
        # File handler with rotation
        if self.enable_file:
            log_file = self.log_dir / 'application.log'
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(self._get_formatter())
            root_logger.addHandler(file_handler)
            self.handlers['file'] = file_handler
            
            # Separate error log file
            error_log_file = self.log_dir / 'error.log'
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(self._get_formatter())
            root_logger.addHandler(error_handler)
            self.handlers['error'] = error_handler
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name.
        
        Args:
            name: Name of the logger (typically __name__ of the module).
        
        Returns:
            Configured logger instance.
        
        Example:
            >>> logger = logger_mgr.get_logger(__name__)
            >>> logger.info('Processing started')
        """
        if name in self._loggers:
            return self._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)
        self._loggers[name] = logger
        
        return logger
    
    def set_level(self, level: Union[str, int], logger_name: Optional[str] = None) -> None:
        """Set logging level for a specific logger or all loggers.
        
        Args:
            level: New logging level.
            logger_name: Name of logger to update, or None for all loggers.
        
        Example:
            >>> logger_mgr.set_level('DEBUG')
            >>> logger_mgr.set_level(logging.ERROR, 'myapp.module')
        """
        new_level = self._parse_log_level(level)
        
        if logger_name:
            logger = logging.getLogger(logger_name)
            logger.setLevel(new_level)
        else:
            # Update root logger and all handlers
            logging.getLogger().setLevel(new_level)
            for handler in self.handlers.values():
                if handler != self.handlers.get('error'):  # Keep error handler at ERROR
                    handler.setLevel(new_level)
    
    def add_file_handler(
        self,
        filename: str,
        level: Union[str, int] = logging.INFO,
        format_style: Optional[str] = None
    ) -> None:
        """Add an additional file handler.
        
        Args:
            filename: Name of the log file.
            level: Logging level for this handler.
            format_style: Format style for this handler (uses default if None).
        
        Example:
            >>> logger_mgr.add_file_handler('custom.log', level='DEBUG')
        """
        log_file = self.log_dir / filename
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        handler.setLevel(self._parse_log_level(level))
        
        if format_style:
            original_style = self.format_style
            self.format_style = format_style
            handler.setFormatter(self._get_formatter())
            self.format_style = original_style
        else:
            handler.setFormatter(self._get_formatter())
        
        logging.getLogger().addHandler(handler)
        self.handlers[filename] = handler
    
    def log_exception(self, logger: logging.Logger, message: str = "Exception occurred") -> None:
        """Log an exception with traceback.
        
        Args:
            logger: Logger instance to use.
            message: Custom message for the exception.
        
        Example:
            >>> try:
            ...     risky_operation()
            ... except Exception:
            ...     logger_mgr.log_exception(logger, "Operation failed")
        """
        logger.exception(message)
    
    def shutdown(self) -> None:
        """Shutdown all logging handlers gracefully.
        
        Example:
            >>> logger_mgr.shutdown()
        """
        logging.shutdown()
    
    def __repr__(self) -> str:
        """Return string representation of LoggerManager."""
        return (
            f"LoggerManager(log_dir='{self.log_dir}', "
            f"log_level={logging.getLevelName(self.log_level)}, "
            f"handlers={list(self.handlers.keys())})"
        )


def setup_logger(
    name: str = __name__,
    log_dir: Union[str, Path] = 'logs',
    log_level: Union[str, int] = logging.INFO,
    format_style: str = 'default',
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """Convenience function to set up and get a logger.
    
    Args:
        name: Name of the logger.
        log_dir: Directory for log files.
        log_level: Logging level.
        format_style: Log format style ('default', 'detailed', or 'json').
        enable_console: Enable console logging.
        enable_file: Enable file logging.
    
    Returns:
        Configured logger instance.
    
    Example:
        >>> logger = setup_logger('myapp', log_level='DEBUG')
        >>> logger.info('Application initialized')
    """
    manager = LoggerManager(
        log_dir=log_dir,
        log_level=log_level,
        format_style=format_style,
        enable_console=enable_console,
        enable_file=enable_file
    )
    return manager.get_logger(name)


def get_logger(name: str = __name__) -> logging.Logger:
    """Get a logger with the given name using existing LoggerManager.
    
    Args:
        name: Name of the logger (typically __name__ of the module).
    
    Returns:
        Logger instance.
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug('Debug message')
    """
    manager = LoggerManager()
    return manager.get_logger(name)
