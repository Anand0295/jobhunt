"""Configuration Manager Module.

This module provides centralized configuration management with support for
multiple configuration sources (environment variables, files, defaults),
validation, and type conversion.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
import logging


logger = logging.getLogger(__name__)


@dataclass
class ConfigSchema:
    """Configuration schema definition for validation."""
    
    required_keys: list = field(default_factory=list)
    optional_keys: dict = field(default_factory=dict)
    type_mappings: dict = field(default_factory=dict)


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class ConfigManager:
    """Centralized configuration manager with validation and multiple source support.
    
    Supports loading configuration from:
    - Environment variables
    - JSON files
    - YAML files
    - Dictionary defaults
    
    Attributes:
        config (Dict[str, Any]): The merged configuration dictionary.
        schema (Optional[ConfigSchema]): Schema for validation.
    
    Example:
        >>> config_mgr = ConfigManager()
        >>> config_mgr.load_from_env(prefix='APP_')
        >>> config_mgr.load_from_file('config.yaml')
        >>> api_key = config_mgr.get('api_key', required=True)
    """
    
    def __init__(self, schema: Optional[ConfigSchema] = None):
        """Initialize the configuration manager.
        
        Args:
            schema: Optional schema for configuration validation.
        """
        self.config: Dict[str, Any] = {}
        self.schema = schema
        self._loaded_sources = []
        logger.info("ConfigManager initialized")
    
    def load_from_env(self, prefix: str = '', lowercase: bool = True) -> None:
        """Load configuration from environment variables.
        
        Args:
            prefix: Prefix for environment variables to load (e.g., 'APP_').
            lowercase: Convert keys to lowercase.
        
        Example:
            >>> config_mgr.load_from_env(prefix='JOBHUNT_')
        """
        logger.info(f"Loading configuration from environment with prefix '{prefix}'")
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                clean_key = key[len(prefix):]
                if lowercase:
                    clean_key = clean_key.lower()
                
                # Attempt type conversion
                self.config[clean_key] = self._convert_type(value)
                logger.debug(f"Loaded env var: {clean_key}")
        
        self._loaded_sources.append(f"environment(prefix={prefix})")
    
    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """Load configuration from a file (JSON or YAML).
        
        Args:
            file_path: Path to the configuration file.
        
        Raises:
            ConfigurationError: If file doesn't exist or has invalid format.
        
        Example:
            >>> config_mgr.load_from_file('config/settings.yaml')
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"Configuration file not found: {file_path}")
            raise ConfigurationError(f"Configuration file not found: {file_path}")
        
        logger.info(f"Loading configuration from file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif file_path.suffix == '.json':
                    data = json.load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported file format: {file_path.suffix}"
                    )
            
            if not isinstance(data, dict):
                raise ConfigurationError("Configuration file must contain a dictionary")
            
            self.config.update(data)
            self._loaded_sources.append(str(file_path))
            logger.info(f"Successfully loaded {len(data)} configuration items")
            
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse configuration file: {e}")
            raise ConfigurationError(f"Failed to parse configuration file: {e}")
    
    def load_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Load configuration from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values.
        
        Example:
            >>> config_mgr.load_from_dict({'debug': True, 'port': 8080})
        """
        logger.info(f"Loading configuration from dictionary with {len(config_dict)} items")
        self.config.update(config_dict)
        self._loaded_sources.append("dictionary")
    
    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key to retrieve.
            default: Default value if key is not found.
            required: If True, raises error when key is missing.
        
        Returns:
            The configuration value.
        
        Raises:
            ConfigurationError: If required key is missing.
        
        Example:
            >>> api_key = config_mgr.get('api_key', required=True)
            >>> debug = config_mgr.get('debug', default=False)
        """
        if key not in self.config:
            if required:
                logger.error(f"Required configuration key missing: {key}")
                raise ConfigurationError(f"Required configuration key missing: {key}")
            logger.debug(f"Configuration key '{key}' not found, using default: {default}")
            return default
        
        return self.config[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key to set.
            value: Value to set.
        
        Example:
            >>> config_mgr.set('max_retries', 3)
        """
        logger.debug(f"Setting configuration: {key} = {value}")
        self.config[key] = value
    
    def validate(self) -> bool:
        """Validate configuration against the schema.
        
        Returns:
            True if validation passes.
        
        Raises:
            ConfigurationError: If validation fails.
        
        Example:
            >>> config_mgr.validate()
        """
        if not self.schema:
            logger.warning("No schema defined for validation")
            return True
        
        logger.info("Validating configuration")
        
        # Check required keys
        for key in self.schema.required_keys:
            if key not in self.config:
                raise ConfigurationError(f"Required configuration key missing: {key}")
        
        # Check types
        for key, expected_type in self.schema.type_mappings.items():
            if key in self.config:
                value = self.config[key]
                if not isinstance(value, expected_type):
                    raise ConfigurationError(
                        f"Configuration key '{key}' has wrong type. "
                        f"Expected {expected_type.__name__}, got {type(value).__name__}"
                    )
        
        logger.info("Configuration validation passed")
        return True
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values.
        
        Returns:
            Dictionary containing all configuration.
        
        Example:
            >>> all_config = config_mgr.get_all()
        """
        return self.config.copy()
    
    def reload(self) -> None:
        """Clear and reload configuration from all previously loaded sources.
        
        Example:
            >>> config_mgr.reload()
        """
        logger.info("Reloading configuration")
        sources = self._loaded_sources.copy()
        self.config.clear()
        self._loaded_sources.clear()
        
        for source in sources:
            if source.startswith('environment'):
                prefix = source.split('prefix=')[1].rstrip(')')
                self.load_from_env(prefix=prefix)
            elif source == 'dictionary':
                logger.warning("Cannot reload from dictionary source")
            else:
                self.load_from_file(source)
    
    def _convert_type(self, value: str) -> Any:
        """Convert string value to appropriate type.
        
        Args:
            value: String value to convert.
        
        Returns:
            Converted value (bool, int, float, or str).
        """
        # Boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
        
        # Integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float
        try:
            return float(value)
        except ValueError:
            pass
        
        # String (default)
        return value
    
    def __repr__(self) -> str:
        """Return string representation of ConfigManager."""
        return f"ConfigManager(items={len(self.config)}, sources={self._loaded_sources})"


def create_default_config() -> ConfigManager:
    """Create a ConfigManager with default jobhunt application settings.
    
    Returns:
        Configured ConfigManager instance with defaults.
    
    Example:
        >>> config = create_default_config()
        >>> config.load_from_env(prefix='JOBHUNT_')
    """
    defaults = {
        'debug': False,
        'log_level': 'INFO',
        'max_retries': 3,
        'timeout': 30,
        'database_url': 'sqlite:///jobhunt.db',
    }
    
    config_mgr = ConfigManager()
    config_mgr.load_from_dict(defaults)
    logger.info("Created default configuration")
    
    return config_mgr
