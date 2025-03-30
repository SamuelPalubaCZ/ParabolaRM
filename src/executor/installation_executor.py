#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Installation Executor for Parabola RM

This module coordinates the entire installation process.
"""

import os
import sys
import logging
import tempfile
import shutil
import time
from typing import Dict, Any, List, Optional, Tuple

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.config_manager.config_manager import ConfigManager
from src.cross_env.env_manager import CrossEnvManager
from src.builders.bootloader.uboot_builder import UBootBuilder
from src.builders.kernel.kernel_builder import KernelBuilder
from src.builders.partition.partition_manager import PartitionManager
from src.installers.system.system_installer import SystemInstaller
from src.installers.desktop.desktop_configurator import DesktopConfigurator

logger = logging.getLogger(__name__)

class InstallationExecutor:
    """
    Installation Executor
    
    This class coordinates the entire installation process.
    """
    
    def __init__(self, config_manager: ConfigManager, env_manager: CrossEnvManager):
        """
        Initialize the Installation Executor
        
        Args:
            config_manager: Configuration manager
            env_manager: Cross-compilation environment manager
        """
        self.config_manager = config_manager
        self.env_manager = env_manager
        self.config = config_manager.get_config()
        
        # Create component instances
        self.bootloader_builder = UBootBuilder(self.config, self.env_manager)
        self.kernel_builder = KernelBuilder(self.config, self.env_manager)
        self.partition_manager = PartitionManager(self.config, self.env_manager)
        self.system_installer = SystemInstaller(self.config, self.env_manager)
        self.desktop_configurator = DesktopConfigurator(self.config, self.env_manager)
        
        # Set up paths
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'output'
        )
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def execute(self, device: str, skip_build: bool = False) -> bool:
        """
        Execute the installation process
        
        Args:
            device: Device to install to (e.g., /dev/mmcblk1)
            skip_build: Whether to skip building components
        
        Returns:
            True if the installation was successful, False otherwise
        """
        try:
            logger.info("Starting installation process...")
            
            # Build components if not skipped
            if not skip_build:
                if not self._build_components():
                    return False
            
            # Partition and format the device
            if not self._partition_and_format(device):
                return False
            
            # Install the bootloader
            if not self._install_bootloader(device):
                return False
            
            # Mount partitions
            mount_points = self._create_mount_points()
            
            if not self.partition_manager.mount_partitions(device, mount_points):
                return False
            
            try:
                # Install the system
                if not self._install_system(mount_points):
                    return False
                
                # Install and configure the desktop environment
                if not self._install_desktop(mount_points):
                    return False
            finally:
                # Unmount partitions
                mount_point_paths = [mount_points[p] for p in sorted(mount_points.keys(), reverse=True)]
                self.partition_manager.unmount_partitions(mount_point_paths)
            
            logger.info("Installation completed successfully")
            return True
        except Exception as e:
            logger.error("Error executing installation: %s", str(e))
            return False
    
    def _build_components(self) -> bool:
        """
        Build all components
        
        Returns:
            True if all components were built successfully, False otherwise
        """
        try:
            logger.info("Building components...")
            
            # Build the bootloader
            logger.info("Building bootloader...")
            if not self.bootloader_builder.build():
                logger.error("Failed to build bootloader")
                return False
            
            # Build the kernel
            logger.info("Building kernel...")
            if not self.kernel_builder.build():
                logger.error("Failed to build kernel")
                return False
            
            logger.info("Components built successfully")
            return True
        except Exception as e:
            logger.error("Error building components: %s", str(e))
            return False
    
    def _partition_and_format(self, device: str) -> bool:
        """
        Partition and format the device
        
        Args:
            device: Device to partition and format
        
        Returns:
            True if the device was partitioned and formatted successfully, False otherwise
        """
        try:
            logger.info("Partitioning and formatting device...")
            
            # Partition the device
            if not self.partition_manager.partition_device(device):
                logger.error("Failed to partition device")
                return False
            
            # Wait for the kernel to recognize the new partition table
            logger.info("Waiting for the kernel to recognize the new partition table...")
            time.sleep(2)
            
            # Format the partitions
            if not self.partition_manager.format_partitions(device):
                logger.error("Failed to format partitions")
                return False
            
            logger.info("Device partitioned and formatted successfully")
            return True
        except Exception as e:
            logger.error("Error partitioning and formatting device: %s", str(e))
            return False
    
    def _install_bootloader(self, device: str) -> bool:
        """
        Install the bootloader
        
        Args:
            device: Device to install the bootloader to
        
        Returns:
            True if the bootloader was installed successfully, False otherwise
        """
        try:
            logger.info("Installing bootloader...")
            
            # Get the bootloader binary path
            bootloader_path = self.bootloader_builder.get_output_path()
            
            # Install the bootloader
            if not self.partition_manager.install_bootloader(device, bootloader_path):
                logger.error("Failed to install bootloader")
                return False
            
            logger.info("Bootloader installed successfully")
            return True
        except Exception as e:
            logger.error("Error installing bootloader: %s", str(e))
            return False
    
    def _create_mount_points(self) -> Dict[int, str]:
        """
        Create mount points for the partitions
        
        Returns:
            Dictionary of partition numbers to mount points
        """
        # Create temporary mount points
        mount_dir = os.path.join(self.output_dir, 'mnt')
        os.makedirs(mount_dir, exist_ok=True)
        
        mount_points = {
            1: os.path.join(mount_dir, 'p1'),  # FAT partition
            2: os.path.join(mount_dir, 'p2'),  # System partition
            3: os.path.join(mount_dir, 'p3')   # Home partition
        }
        
        # Create the mount point directories
        for mount_point in mount_points.values():
            os.makedirs(mount_point, exist_ok=True)
        
        return mount_points
    
    def _install_system(self, mount_points: Dict[int, str]) -> bool:
        """
        Install the system
        
        Args:
            mount_points: Dictionary of partition numbers to mount points
        
        Returns:
            True if the system was installed successfully, False otherwise
        """
        try:
            logger.info("Installing system...")
            
            # Get the kernel files
            kernel_files = self.kernel_builder.get_output_paths()
            
            # Get the bootloader files
            bootloader_files = {
                'waveform': kernel_files['waveform']
            }
            
            # Install the system
            if not self.system_installer.install(mount_points, kernel_files, bootloader_files):
                logger.error("Failed to install system")
                return False
            
            logger.info("System installed successfully")
            return True
        except Exception as e:
            logger.error("Error installing system: %s", str(e))
            return False
    
    def _install_desktop(self, mount_points: Dict[int, str]) -> bool:
        """
        Install and configure the desktop environment
        
        Args:
            mount_points: Dictionary of partition numbers to mount points
        
        Returns:
            True if the desktop environment was installed and configured successfully, False otherwise
        """
        try:
            logger.info("Installing and configuring desktop environment...")
            
            # Install and configure the desktop environment
            if not self.desktop_configurator.install(mount_points[2]):
                logger.error("Failed to install and configure desktop environment")
                return False
            
            # Configure battery monitor
            if not self.desktop_configurator.configure_battery_monitor(mount_points[2]):
                logger.warning("Failed to configure battery monitor")
                # Continue anyway, this is not critical
            
            # Configure automatic login
            if not self.system_installer.configure_auto_login(mount_points[2]):
                logger.warning("Failed to configure automatic login")
                # Continue anyway, this is not critical
            
            # Configure graceful shutdown
            if not self.system_installer.configure_shutdown(mount_points[2]):
                logger.warning("Failed to configure graceful shutdown")
                # Continue anyway, this is not critical
            
            logger.info("Desktop environment installed and configured successfully")
            return True
        except Exception as e:
            logger.error("Error installing and configuring desktop environment: %s", str(e))
            return False