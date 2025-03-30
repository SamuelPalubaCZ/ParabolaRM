#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration Manager for Parabola RM Builder

This module handles loading, validating, and managing the configuration for the builder.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Configuration Manager for Parabola RM Builder
    
    This class is responsible for loading, validating, and managing the configuration
    for the Parabola RM Builder.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Configuration Manager
        
        Args:
            config_path: Path to the configuration file. If None, the default
                         configuration will be used.
        """
        self.config_path = config_path
        self.config = {}
        self.default_config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config',
            'default.yaml'
        )
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load the configuration from the specified path or the default configuration
        
        Returns:
            The loaded configuration as a dictionary
        """
        # Load default configuration
        try:
            with open(self.default_config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                logger.debug("Loaded default configuration from %s", self.default_config_path)
        except Exception as e:
            logger.error("Failed to load default configuration: %s", str(e))
            raise
        
        # Load user configuration if specified
        if self.config_path:
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    logger.debug("Loaded user configuration from %s", self.config_path)
                    
                    # Merge user configuration with default configuration
                    self._merge_configs(self.config, user_config)
            except Exception as e:
                logger.error("Failed to load user configuration: %s", str(e))
                raise
        
        return self.config
    
    def _merge_configs(self, default_config: Dict[str, Any], user_config: Dict[str, Any]) -> None:
        """
        Merge user configuration with default configuration
        
        Args:
            default_config: Default configuration dictionary
            user_config: User configuration dictionary
        """
        for key, value in user_config.items():
            if (
                key in default_config and 
                isinstance(default_config[key], dict) and 
                isinstance(value, dict)
            ):
                self._merge_configs(default_config[key], value)
            else:
                default_config[key] = value
    
    def validate_config(self) -> bool:
        """
        Validate the configuration
        
        Returns:
            True if the configuration is valid, False otherwise
        """
        # TODO: Implement validation logic
        return True
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration
        
        Returns:
            The current configuration as a dictionary
        """
        return self.config
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a value from the configuration using a dot-separated key path
        
        Args:
            key_path: Dot-separated key path (e.g., 'cross_compilation.environment_type')
            default: Default value to return if the key is not found
        
        Returns:
            The value at the specified key path, or the default value if not found
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set_value(self, key_path: str, value: Any) -> None:
        """
        Set a value in the configuration using a dot-separated key path
        
        Args:
            key_path: Dot-separated key path (e.g., 'cross_compilation.environment_type')
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        for i, key in enumerate(keys[:-1]):
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save_config(self, output_path: str) -> None:
        """
        Save the current configuration to a file
        
        Args:
            output_path: Path to save the configuration to
        """
        try:
            with open(output_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
                logger.debug("Saved configuration to %s", output_path)
        except Exception as e:
            logger.error("Failed to save configuration: %s", str(e))
            raise