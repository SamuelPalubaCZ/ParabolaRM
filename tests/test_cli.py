#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for the CLI module
"""

import os
import sys
import unittest
import tempfile
import yaml
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import src.cli as cli

class TestCLI(unittest.TestCase):
    """
    Tests for the CLI module
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
    
    def test_setup_argparse(self):
        """
        Test setting up the argument parser
        """
        # Set up the argument parser
        parser = cli.setup_argparse()
        
        # Check that the parser has the expected commands
        self.assertIn('init', parser._subparsers._group_actions[0].choices)
        self.assertIn('build', parser._subparsers._group_actions[0].choices)
        self.assertIn('install', parser._subparsers._group_actions[0].choices)
        self.assertIn('env', parser._subparsers._group_actions[0].choices)
    
    @patch('src.cli.ConfigManager')
    def test_init_config(self, mock_config_manager):
        """
        Test initializing a configuration
        """
        # Create a mock ConfigManager
        mock_config_manager_instance = MagicMock()
        mock_config_manager.return_value = mock_config_manager_instance
        
        # Create mock arguments
        args = MagicMock()
        args.output = self.test_config_path
        
        # Call the init_config function
        result = cli.init_config(args, mock_config_manager_instance)
        
        # Check that the function returned success
        self.assertEqual(result, 0)
        
        # Check that the ConfigManager methods were called
        mock_config_manager_instance.load_config.assert_called_once()
        mock_config_manager_instance.save_config.assert_called_once_with(self.test_config_path)
    
    @patch('src.cli.CrossEnvManager')
    @patch('src.cli.ConfigManager')
    def test_setup_environment(self, mock_config_manager, mock_cross_env_manager):
        """
        Test setting up the environment
        """
        # Create a mock ConfigManager
        mock_config_manager_instance = MagicMock()
        mock_config_manager_instance.load_config.return_value = self.test_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        # Create a mock CrossEnvManager
        mock_cross_env_manager_instance = MagicMock()
        mock_cross_env_manager_instance.setup_environment.return_value = True
        mock_cross_env_manager.return_value = mock_cross_env_manager_instance
        
        # Create mock arguments
        args = MagicMock()
        args.config = self.test_config_path
        
        # Call the setup_environment function
        result = cli.setup_environment(args, mock_config_manager_instance)
        
        # Check that the function returned success
        self.assertEqual(result, 0)
        
        # Check that the ConfigManager and CrossEnvManager methods were called
        mock_config_manager_instance.load_config.assert_called_once()
        mock_cross_env_manager.assert_called_once_with(self.test_config)
        mock_cross_env_manager_instance.setup_environment.assert_called_once()
    
    @patch('src.cli.InstallationExecutor')
    @patch('src.cli.CrossEnvManager')
    @patch('src.cli.ConfigManager')
    def test_build_components_all(self, mock_config_manager, mock_cross_env_manager, mock_installation_executor):
        """
        Test building all components
        """
        # Create a mock ConfigManager
        mock_config_manager_instance = MagicMock()
        mock_config_manager_instance.load_config.return_value = self.test_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        # Create a mock CrossEnvManager
        mock_cross_env_manager_instance = MagicMock()
        mock_cross_env_manager_instance.setup_environment.return_value = True
        mock_cross_env_manager.return_value = mock_cross_env_manager_instance
        
        # Create a mock InstallationExecutor
        mock_installation_executor_instance = MagicMock()
        mock_installation_executor_instance._build_components.return_value = True
        mock_installation_executor.return_value = mock_installation_executor_instance
        
        # Create mock arguments
        args = MagicMock()
        args.config = self.test_config_path
        args.all = True
        args.bootloader = False
        args.kernel = False
        
        # Call the build_components function
        result = cli.build_components(args, mock_config_manager_instance)
        
        # Check that the function returned success
        self.assertEqual(result, 0)
        
        # Check that the ConfigManager, CrossEnvManager, and InstallationExecutor methods were called
        mock_config_manager_instance.load_config.assert_called_once()
        mock_cross_env_manager.assert_called_once_with(self.test_config)
        mock_cross_env_manager_instance.setup_environment.assert_called_once()
        mock_installation_executor.assert_called_once_with(mock_config_manager_instance, mock_cross_env_manager_instance)
        mock_installation_executor_instance._build_components.assert_called_once()
    
    @patch('src.cli.UBootBuilder')
    @patch('src.cli.CrossEnvManager')
    @patch('src.cli.ConfigManager')
    def test_build_components_bootloader(self, mock_config_manager, mock_cross_env_manager, mock_uboot_builder):
        """
        Test building the bootloader
        """
        # Create a mock ConfigManager
        mock_config_manager_instance = MagicMock()
        mock_config_manager_instance.load_config.return_value = self.test_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        # Create a mock CrossEnvManager
        mock_cross_env_manager_instance = MagicMock()
        mock_cross_env_manager_instance.setup_environment.return_value = True
        mock_cross_env_manager.return_value = mock_cross_env_manager_instance
        
        # Create a mock UBootBuilder
        mock_uboot_builder_instance = MagicMock()
        mock_uboot_builder_instance.build.return_value = True
        mock_uboot_builder.return_value = mock_uboot_builder_instance
        
        # Create mock arguments
        args = MagicMock()
        args.config = self.test_config_path
        args.all = False
        args.bootloader = True
        args.kernel = False
        
        # Call the build_components function
        result = cli.build_components(args, mock_config_manager_instance)
        
        # Check that the function returned success
        self.assertEqual(result, 0)
        
        # Check that the ConfigManager, CrossEnvManager, and UBootBuilder methods were called
        mock_config_manager_instance.load_config.assert_called_once()
        mock_cross_env_manager.assert_called_once_with(self.test_config)
        mock_cross_env_manager_instance.setup_environment.assert_called_once()
        mock_uboot_builder.assert_called_once_with(self.test_config, mock_cross_env_manager_instance)
        mock_uboot_builder_instance.build.assert_called_once()
    
    @patch('src.cli.InstallationExecutor')
    @patch('src.cli.CrossEnvManager')
    @patch('src.cli.ConfigManager')
    def test_install_parabola(self, mock_config_manager, mock_cross_env_manager, mock_installation_executor):
        """
        Test installing Parabola RM
        """
        # Create a mock ConfigManager
        mock_config_manager_instance = MagicMock()
        mock_config_manager_instance.load_config.return_value = self.test_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        # Create a mock CrossEnvManager
        mock_cross_env_manager_instance = MagicMock()
        mock_cross_env_manager_instance.setup_environment.return_value = True
        mock_cross_env_manager.return_value = mock_cross_env_manager_instance
        
        # Create a mock InstallationExecutor
        mock_installation_executor_instance = MagicMock()
        mock_installation_executor_instance.execute.return_value = True
        mock_installation_executor.return_value = mock_installation_executor_instance
        
        # Create mock arguments
        args = MagicMock()
        args.config = self.test_config_path
        args.device = '/dev/mmcblk1'
        args.skip_build = False
        
        # Call the install_parabola function
        result = cli.install_parabola(args, mock_config_manager_instance)
        
        # Check that the function returned success
        self.assertEqual(result, 0)
        
        # Check that the ConfigManager, CrossEnvManager, and InstallationExecutor methods were called
        mock_config_manager_instance.load_config.assert_called_once()
        mock_cross_env_manager.assert_called_once_with(self.test_config)
        mock_cross_env_manager_instance.setup_environment.assert_called_once()
        mock_installation_executor.assert_called_once_with(mock_config_manager_instance, mock_cross_env_manager_instance)
        mock_installation_executor_instance.execute.assert_called_once_with('/dev/mmcblk1', False)

if __name__ == '__main__':
    unittest.main()