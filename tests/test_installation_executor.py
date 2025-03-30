#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for the Installation Executor
"""

import os
import sys
import unittest
import tempfile
import yaml
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.executor.installation_executor import InstallationExecutor

class TestInstallationExecutor(unittest.TestCase):
    """
    Tests for the Installation Executor
    """
    
    def setUp(self):
        """
        Set up the test
        """
        # Create a test configuration
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
            },
            'partition': {
                'layout': {
                    'fat_size': 20,
                    'system_size': 2,
                    'home_size': 0
                }
            }
        }
        
        # Create mock objects
        self.mock_config_manager = MagicMock()
        self.mock_config_manager.get_config.return_value = self.test_config
        
        self.mock_env_manager = MagicMock()
        
        self.mock_bootloader_builder = MagicMock()
        self.mock_kernel_builder = MagicMock()
        self.mock_partition_manager = MagicMock()
        self.mock_system_installer = MagicMock()
        self.mock_desktop_configurator = MagicMock()
    
    @patch('src.executor.installation_executor.UBootBuilder')
    @patch('src.executor.installation_executor.KernelBuilder')
    @patch('src.executor.installation_executor.PartitionManager')
    @patch('src.executor.installation_executor.SystemInstaller')
    @patch('src.executor.installation_executor.DesktopConfigurator')
    def test_init(self, mock_desktop_configurator, mock_system_installer, mock_partition_manager, mock_kernel_builder, mock_bootloader_builder):
        """
        Test initialization of the Installation Executor
        """
        # Set up the mock objects
        mock_bootloader_builder.return_value = self.mock_bootloader_builder
        mock_kernel_builder.return_value = self.mock_kernel_builder
        mock_partition_manager.return_value = self.mock_partition_manager
        mock_system_installer.return_value = self.mock_system_installer
        mock_desktop_configurator.return_value = self.mock_desktop_configurator
        
        # Create an Installation Executor
        executor = InstallationExecutor(self.mock_config_manager, self.mock_env_manager)
        
        # Check that the objects were created correctly
        self.assertEqual(executor.config_manager, self.mock_config_manager)
        self.assertEqual(executor.env_manager, self.mock_env_manager)
        self.assertEqual(executor.config, self.test_config)
        
        # Check that the builders and installers were created correctly
        mock_bootloader_builder.assert_called_once_with(self.test_config, self.mock_env_manager)
        mock_kernel_builder.assert_called_once_with(self.test_config, self.mock_env_manager)
        mock_partition_manager.assert_called_once_with(self.test_config, self.mock_env_manager)
        mock_system_installer.assert_called_once_with(self.test_config, self.mock_env_manager)
        mock_desktop_configurator.assert_called_once_with(self.test_config, self.mock_env_manager)
    
    @patch('src.executor.installation_executor.UBootBuilder')
    @patch('src.executor.installation_executor.KernelBuilder')
    @patch('src.executor.installation_executor.PartitionManager')
    @patch('src.executor.installation_executor.SystemInstaller')
    @patch('src.executor.installation_executor.DesktopConfigurator')
    def test_build_components(self, mock_desktop_configurator, mock_system_installer, mock_partition_manager, mock_kernel_builder, mock_bootloader_builder):
        """
        Test building components
        """
        # Set up the mock objects
        mock_bootloader_builder.return_value = self.mock_bootloader_builder
        mock_kernel_builder.return_value = self.mock_kernel_builder
        mock_partition_manager.return_value = self.mock_partition_manager
        mock_system_installer.return_value = self.mock_system_installer
        mock_desktop_configurator.return_value = self.mock_desktop_configurator
        
        # Set up the mock builders
        self.mock_bootloader_builder.build.return_value = True
        self.mock_kernel_builder.build.return_value = True
        
        # Create an Installation Executor
        executor = InstallationExecutor(self.mock_config_manager, self.mock_env_manager)
        
        # Build the components
        result = executor._build_components()
        
        # Check that the function returned success
        self.assertTrue(result)
        
        # Check that the builders were called
        self.mock_bootloader_builder.build.assert_called_once()
        self.mock_kernel_builder.build.assert_called_once()
    
    @patch('src.executor.installation_executor.UBootBuilder')
    @patch('src.executor.installation_executor.KernelBuilder')
    @patch('src.executor.installation_executor.PartitionManager')
    @patch('src.executor.installation_executor.SystemInstaller')
    @patch('src.executor.installation_executor.DesktopConfigurator')
    def test_build_components_bootloader_failure(self, mock_desktop_configurator, mock_system_installer, mock_partition_manager, mock_kernel_builder, mock_bootloader_builder):
        """
        Test building components with bootloader failure
        """
        # Set up the mock objects
        mock_bootloader_builder.return_value = self.mock_bootloader_builder
        mock_kernel_builder.return_value = self.mock_kernel_builder
        mock_partition_manager.return_value = self.mock_partition_manager
        mock_system_installer.return_value = self.mock_system_installer
        mock_desktop_configurator.return_value = self.mock_desktop_configurator
        
        # Set up the mock builders
        self.mock_bootloader_builder.build.return_value = False
        
        # Create an Installation Executor
        executor = InstallationExecutor(self.mock_config_manager, self.mock_env_manager)
        
        # Build the components
        result = executor._build_components()
        
        # Check that the function returned failure
        self.assertFalse(result)
        
        # Check that the bootloader builder was called
        self.mock_bootloader_builder.build.assert_called_once()
        
        # Check that the kernel builder was not called
        self.mock_kernel_builder.build.assert_not_called()
    
    @patch('src.executor.installation_executor.UBootBuilder')
    @patch('src.executor.installation_executor.KernelBuilder')
    @patch('src.executor.installation_executor.PartitionManager')
    @patch('src.executor.installation_executor.SystemInstaller')
    @patch('src.executor.installation_executor.DesktopConfigurator')
    def test_partition_and_format(self, mock_desktop_configurator, mock_system_installer, mock_partition_manager, mock_kernel_builder, mock_bootloader_builder):
        """
        Test partitioning and formatting
        """
        # Set up the mock objects
        mock_bootloader_builder.return_value = self.mock_bootloader_builder
        mock_kernel_builder.return_value = self.mock_kernel_builder
        mock_partition_manager.return_value = self.mock_partition_manager
        mock_system_installer.return_value = self.mock_system_installer
        mock_desktop_configurator.return_value = self.mock_desktop_configurator
        
        # Set up the mock partition manager
        self.mock_partition_manager.partition_device.return_value = True
        self.mock_partition_manager.format_partitions.return_value = True
        
        # Create an Installation Executor
        executor = InstallationExecutor(self.mock_config_manager, self.mock_env_manager)
        
        # Partition and format
        result = executor._partition_and_format('/dev/mmcblk1')
        
        # Check that the function returned success
        self.assertTrue(result)
        
        # Check that the partition manager was called
        self.mock_partition_manager.partition_device.assert_called_once_with('/dev/mmcblk1')
        self.mock_partition_manager.format_partitions.assert_called_once_with('/dev/mmcblk1')
    
    @patch('src.executor.installation_executor.UBootBuilder')
    @patch('src.executor.installation_executor.KernelBuilder')
    @patch('src.executor.installation_executor.PartitionManager')
    @patch('src.executor.installation_executor.SystemInstaller')
    @patch('src.executor.installation_executor.DesktopConfigurator')
    @patch('src.executor.installation_executor.time.sleep')
    def test_execute(self, mock_sleep, mock_desktop_configurator, mock_system_installer, mock_partition_manager, mock_kernel_builder, mock_bootloader_builder):
        """
        Test executing the installation
        """
        # Set up the mock objects
        mock_bootloader_builder.return_value = self.mock_bootloader_builder
        mock_kernel_builder.return_value = self.mock_kernel_builder
        mock_partition_manager.return_value = self.mock_partition_manager
        mock_system_installer.return_value = self.mock_system_installer
        mock_desktop_configurator.return_value = self.mock_desktop_configurator
        
        # Set up the mock builders and installers
        self.mock_bootloader_builder.build.return_value = True
        self.mock_kernel_builder.build.return_value = True
        self.mock_bootloader_builder.get_output_path.return_value = '/tmp/u-boot.imx'
        self.mock_kernel_builder.get_output_paths.return_value = {
            'zImage': '/tmp/zImage',
            'dtb': '/tmp/zero-gravitas.dtb',
            'waveform': '/tmp/epdc_ES103CS1.fw.ihex'
        }
        self.mock_partition_manager.partition_device.return_value = True
        self.mock_partition_manager.format_partitions.return_value = True
        self.mock_partition_manager.install_bootloader.return_value = True
        self.mock_partition_manager.mount_partitions.return_value = True
        self.mock_partition_manager.unmount_partitions.return_value = True
        self.mock_system_installer.install.return_value = True
        self.mock_desktop_configurator.install.return_value = True
        
        # Create an Installation Executor
        executor = InstallationExecutor(self.mock_config_manager, self.mock_env_manager)
        
        # Execute the installation
        result = executor.execute('/dev/mmcblk1', False)
        
        # Check that the function returned success
        self.assertTrue(result)
        
        # Check that the builders and installers were called
        self.mock_bootloader_builder.build.assert_called_once()
        self.mock_kernel_builder.build.assert_called_once()
        self.mock_partition_manager.partition_device.assert_called_once_with('/dev/mmcblk1')
        self.mock_partition_manager.format_partitions.assert_called_once_with('/dev/mmcblk1')
        self.mock_partition_manager.install_bootloader.assert_called_once_with('/dev/mmcblk1', '/tmp/u-boot.imx')
        self.mock_partition_manager.mount_partitions.assert_called_once()
        self.mock_system_installer.install.assert_called_once()
        self.mock_desktop_configurator.install.assert_called_once()
        self.mock_partition_manager.unmount_partitions.assert_called_once()

if __name__ == '__main__':
    unittest.main()