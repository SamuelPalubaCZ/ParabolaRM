#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Installation Verifier for Parabola RM

This module verifies that the installation was successful.
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

from src.cross_env.env_manager import CrossEnvManager

logger = logging.getLogger(__name__)

class InstallationVerifier:
    """
    Installation Verifier
    
    This class verifies that the installation was successful.
    """
    
    def __init__(self, config: Dict[str, Any], env_manager: CrossEnvManager):
        """
        Initialize the Installation Verifier
        
        Args:
            config: Configuration dictionary
            env_manager: Cross-compilation environment manager
        """
        self.config = config
        self.env_manager = env_manager
    
    def verify(self, device: str) -> bool:
        """
        Verify the installation
        
        Args:
            device: Device to verify
        
        Returns:
            True if the installation was verified successfully, False otherwise
        """
        try:
            logger.info("Verifying installation...")
            
            # Verify the bootloader
            if not self._verify_bootloader(device):
                return False
            
            # Verify the partitions
            if not self._verify_partitions(device):
                return False
            
            # Create temporary mount points
            mount_points = self._create_mount_points()
            
            try:
                # Mount the partitions
                if not self._mount_partitions(device, mount_points):
                    return False
                
                # Verify the system
                if not self._verify_system(mount_points[2]):
                    return False
                
                # Verify the desktop environment
                if not self._verify_desktop(mount_points[2]):
                    return False
            finally:
                # Unmount the partitions
                self._unmount_partitions(list(mount_points.values()))
            
            logger.info("Installation verified successfully")
            return True
        except Exception as e:
            logger.error("Error verifying installation: %s", str(e))
            return False
    
    def _verify_bootloader(self, device: str) -> bool:
        """
        Verify the bootloader
        
        Args:
            device: Device to verify
        
        Returns:
            True if the bootloader was verified successfully, False otherwise
        """
        try:
            logger.info("Verifying bootloader...")
            
            # Check if the bootloader is installed
            boot0_device = f"{device}boot0"
            
            # Check if the boot0 device exists
            returncode, stdout, stderr = self.env_manager.run_command(
                ['ls', boot0_device],
                cwd=None
            )
            
            if returncode != 0:
                logger.error("Boot0 device not found: %s", boot0_device)
                return False
            
            logger.info("Bootloader verified successfully")
            return True
        except Exception as e:
            logger.error("Error verifying bootloader: %s", str(e))
            return False
    
    def _verify_partitions(self, device: str) -> bool:
        """
        Verify the partitions
        
        Args:
            device: Device to verify
        
        Returns:
            True if the partitions were verified successfully, False otherwise
        """
        try:
            logger.info("Verifying partitions...")
            
            # Check if the partitions exist
            for i in range(1, 4):
                partition = f"{device}p{i}"
                
                # Check if the partition exists
                returncode, stdout, stderr = self.env_manager.run_command(
                    ['ls', partition],
                    cwd=None
                )
                
                if returncode != 0:
                    logger.error("Partition not found: %s", partition)
                    return False
            
            logger.info("Partitions verified successfully")
            return True
        except Exception as e:
            logger.error("Error verifying partitions: %s", str(e))
            return False
    
    def _create_mount_points(self) -> Dict[int, str]:
        """
        Create temporary mount points
        
        Returns:
            Dictionary of partition numbers to mount points
        """
        # Create a temporary directory for mount points
        temp_dir = tempfile.mkdtemp()
        
        # Create mount points for each partition
        mount_points = {
            1: os.path.join(temp_dir, 'p1'),
            2: os.path.join(temp_dir, 'p2'),
            3: os.path.join(temp_dir, 'p3')
        }
        
        # Create the mount point directories
        for mount_point in mount_points.values():
            os.makedirs(mount_point, exist_ok=True)
        
        return mount_points
    
    def _mount_partitions(self, device: str, mount_points: Dict[int, str]) -> bool:
        """
        Mount the partitions
        
        Args:
            device: Device to mount
            mount_points: Dictionary of partition numbers to mount points
        
        Returns:
            True if the partitions were mounted successfully, False otherwise
        """
        try:
            logger.info("Mounting partitions...")
            
            # Mount each partition
            for i, mount_point in mount_points.items():
                partition = f"{device}p{i}"
                
                # Mount the partition
                returncode, stdout, stderr = self.env_manager.run_command(
                    ['mount', partition, mount_point],
                    cwd=None
                )
                
                if returncode != 0:
                    logger.error("Failed to mount partition %s: %s", partition, stderr)
                    return False
            
            logger.info("Partitions mounted successfully")
            return True
        except Exception as e:
            logger.error("Error mounting partitions: %s", str(e))
            return False
    
    def _unmount_partitions(self, mount_points: List[str]) -> bool:
        """
        Unmount the partitions
        
        Args:
            mount_points: List of mount points to unmount
        
        Returns:
            True if the partitions were unmounted successfully, False otherwise
        """
        try:
            logger.info("Unmounting partitions...")
            
            # Unmount each partition
            for mount_point in mount_points:
                # Unmount the partition
                returncode, stdout, stderr = self.env_manager.run_command(
                    ['umount', mount_point],
                    cwd=None
                )
                
                if returncode != 0:
                    logger.warning("Failed to unmount %s: %s", mount_point, stderr)
                    # Continue anyway, this is not critical
            
            # Remove the temporary directory
            if os.path.exists(os.path.dirname(mount_points[0])):
                shutil.rmtree(os.path.dirname(mount_points[0]))
            
            logger.info("Partitions unmounted successfully")
            return True
        except Exception as e:
            logger.error("Error unmounting partitions: %s", str(e))
            return False
    
    def _verify_system(self, mount_point: str) -> bool:
        """
        Verify the system
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if the system was verified successfully, False otherwise
        """
        try:
            logger.info("Verifying system...")
            
            # Check if essential system files exist
            essential_files = [
                'boot/zImage',
                'boot/zero-gravitas.dtb',
                'etc/fstab',
                'etc/systemd/network/usb0.network',
                'etc/pam.d/login',
                'etc/pam.d/system-login'
            ]
            
            for file in essential_files:
                file_path = os.path.join(mount_point, file)
                
                if not os.path.exists(file_path):
                    logger.error("Essential system file not found: %s", file)
                    return False
            
            logger.info("System verified successfully")
            return True
        except Exception as e:
            logger.error("Error verifying system: %s", str(e))
            return False
    
    def _verify_desktop(self, mount_point: str) -> bool:
        """
        Verify the desktop environment
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if the desktop environment was verified successfully, False otherwise
        """
        try:
            # Get the desktop environment
            environment = self.config.get('desktop', {}).get('environment', 'xfce')
            
            if environment == 'none':
                logger.info("No desktop environment selected, skipping verification")
                return True
            
            logger.info("Verifying desktop environment...")
            
            # Check if essential desktop files exist
            essential_files = [
                'etc/X11/xorg.conf',
                'root/.xserverrc',
                'root/.xinitrc',
                'root/.bash_profile'
            ]
            
            for file in essential_files:
                file_path = os.path.join(mount_point, file)
                
                if not os.path.exists(file_path):
                    logger.error("Essential desktop file not found: %s", file)
                    return False
            
            # Check if the desktop environment is installed
            if environment == 'xfce':
                xfce_files = [
                    'usr/bin/xfce4-session',
                    'usr/bin/xfwm4',
                    'usr/bin/xfdesktop'
                ]
                
                for file in xfce_files:
                    file_path = os.path.join(mount_point, file)
                    
                    if not os.path.exists(file_path):
                        logger.error("Xfce file not found: %s", file)
                        return False
            
            logger.info("Desktop environment verified successfully")
            return True
        except Exception as e:
            logger.error("Error verifying desktop environment: %s", str(e))
            return False
    
    def generate_report(self, device: str) -> Dict[str, Any]:
        """
        Generate a report of the installation
        
        Args:
            device: Device to generate a report for
        
        Returns:
            Dictionary containing the report
        """
        report = {
            'device': device,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'success': False,
            'bootloader': {
                'verified': False
            },
            'partitions': {
                'verified': False
            },
            'system': {
                'verified': False
            },
            'desktop': {
                'verified': False
            }
        }
        
        try:
            # Verify the bootloader
            report['bootloader']['verified'] = self._verify_bootloader(device)
            
            # Verify the partitions
            report['partitions']['verified'] = self._verify_partitions(device)
            
            # Create temporary mount points
            mount_points = self._create_mount_points()
            
            try:
                # Mount the partitions
                if self._mount_partitions(device, mount_points):
                    # Verify the system
                    report['system']['verified'] = self._verify_system(mount_points[2])
                    
                    # Verify the desktop environment
                    report['desktop']['verified'] = self._verify_desktop(mount_points[2])
            finally:
                # Unmount the partitions
                self._unmount_partitions(list(mount_points.values()))
            
            # Set overall success
            report['success'] = (
                report['bootloader']['verified'] and
                report['partitions']['verified'] and
                report['system']['verified'] and
                report['desktop']['verified']
            )
        except Exception as e:
            logger.error("Error generating report: %s", str(e))
            report['error'] = str(e)
        
        return report