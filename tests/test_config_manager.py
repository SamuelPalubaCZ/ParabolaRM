#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for the Configuration Manager
"""

import os
import sys
import unittest
import tempfile
import yaml

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_manager.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """
    Tests for the Configuration Manager
    """
    
    def setUp(self):
        """
        Set up the test
        """
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a test configuration file
        self.test_config_path = os.path.join(self.temp_dir.name, 'test_config.yaml')
        self.test_config = {
            'cross_compilation': {
                'environment_type': 'container',
                'toolchain_version': 'test',
                'container': {
                    'base_image': 'test:latest'
                }
            },
            'hardware': {
                'tablet_model': 'rm1'
            }
        }
        
        with open(self.test_config_path, 'w') as f:
            yaml.dump(self.test_config, f)
    
    def tearDown(self):
        """
        Clean up after the test
        """
        # Remove the temporary directory
        self.temp_dir.cleanup()
    
    def test_load_config(self):
        """
        Test loading a configuration file
        """
        # Create a configuration manager with the test configuration file
        config_manager = ConfigManager(self.test_config_path)
        
        # Load the configuration
        config = config_manager.load_config()
        
        # Check that the configuration was loaded correctly
        self.assertEqual(config['cross_compilation']['environment_type'], 'container')
        self.assertEqual(config['cross_compilation']['toolchain_version'], 'test')
        self.assertEqual(config['cross_compilation']['container']['base_image'], 'test:latest')
        self.assertEqual(config['hardware']['tablet_model'], 'rm1')
    
    def test_get_value(self):
        """
        Test getting a value from the configuration
        """
        # Create a configuration manager with the test configuration file
        config_manager = ConfigManager(self.test_config_path)
        
        # Load the configuration
        config_manager.load_config()
        
        # Get values from the configuration
        self.assertEqual(
            config_manager.get_value('cross_compilation.environment_type'),
            'container'
        )
        self.assertEqual(
            config_manager.get_value('cross_compilation.toolchain_version'),
            'test'
        )
        self.assertEqual(
            config_manager.get_value('cross_compilation.container.base_image'),
            'test:latest'
        )
        self.assertEqual(
            config_manager.get_value('hardware.tablet_model'),
            'rm1'
        )
        
        # Get a non-existent value
        self.assertIsNone(config_manager.get_value('non_existent_key'))
        
        # Get a non-existent value with a default
        self.assertEqual(
            config_manager.get_value('non_existent_key', 'default_value'),
            'default_value'
        )
    
    def test_set_value(self):
        """
        Test setting a value in the configuration
        """
        # Create a configuration manager with the test configuration file
        config_manager = ConfigManager(self.test_config_path)
        
        # Load the configuration
        config_manager.load_config()
        
        # Set values in the configuration
        config_manager.set_value('cross_compilation.environment_type', 'direct')
        config_manager.set_value('cross_compilation.toolchain_version', 'new_test')
        config_manager.set_value('cross_compilation.container.base_image', 'new_test:latest')
        config_manager.set_value('hardware.tablet_model', 'rm2')
        
        # Check that the values were set correctly
        self.assertEqual(
            config_manager.get_value('cross_compilation.environment_type'),
            'direct'
        )
        self.assertEqual(
            config_manager.get_value('cross_compilation.toolchain_version'),
            'new_test'
        )
        self.assertEqual(
            config_manager.get_value('cross_compilation.container.base_image'),
            'new_test:latest'
        )
        self.assertEqual(
            config_manager.get_value('hardware.tablet_model'),
            'rm2'
        )
        
        # Set a non-existent key
        config_manager.set_value('new_key', 'new_value')
        
        # Check that the new key was set correctly
        self.assertEqual(
            config_manager.get_value('new_key'),
            'new_value'
        )
        
        # Set a nested non-existent key
        config_manager.set_value('new_section.new_key', 'new_value')
        
        # Check that the nested key was set correctly
        self.assertEqual(
            config_manager.get_value('new_section.new_key'),
            'new_value'
        )
    
    def test_save_config(self):
        """
        Test saving a configuration file
        """
        # Create a configuration manager with the test configuration file
        config_manager = ConfigManager(self.test_config_path)
        
        # Load the configuration
        config_manager.load_config()
        
        # Set some values in the configuration
        config_manager.set_value('cross_compilation.environment_type', 'direct')
        config_manager.set_value('new_section.new_key', 'new_value')
        
        # Save the configuration to a new file
        new_config_path = os.path.join(self.temp_dir.name, 'new_config.yaml')
        config_manager.save_config(new_config_path)
        
        # Load the new configuration file
        with open(new_config_path, 'r') as f:
            new_config = yaml.safe_load(f)
        
        # Check that the configuration was saved correctly
        self.assertEqual(new_config['cross_compilation']['environment_type'], 'direct')
        self.assertEqual(new_config['new_section']['new_key'], 'new_value')

if __name__ == '__main__':
    unittest.main()