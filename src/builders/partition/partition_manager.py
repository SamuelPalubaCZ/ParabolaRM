#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Partition Manager for Parabola RM

This module handles the partitioning and formatting of the eMMC storage.
"""

import os
import sys
import logging
import tempfile
import shutil
import re
from typing import Dict, Any, List, Optional, Tuple

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.cross_env.env_manager import CrossEnvManager

logger = logging.getLogger(__name__)

class PartitionManager:
    """
    Partition Manager
    
    This class is responsible for partitioning and formatting the eMMC storage.
    """
    
    def __init__(self, config: Dict[str, Any], env_manager: CrossEnvManager):
        """
        Initialize the Partition Manager
        
        Args:
            config: Configuration dictionary
            env_manager: Cross-compilation environment manager
        """
        self.config = config
        self.env_manager = env_manager
        self.partition_config = config.get('partition', {})
    
    def partition_device(self, device: str) -> bool:
        """
        Partition the device
        
        Args:
            device: Device to partition (e.g., /dev/mmcblk1)
        
        Returns:
            True if the device was partitioned successfully, False otherwise
        """
        try:
            logger.info("Partitioning device: %s", device)
            
            # Get partition layout
            layout = self.partition_config.get('layout', {})
            fat_size = layout.get('fat_size', 20)
            system_size = layout.get('system_size', 2)
            home_size = layout.get('home_size', 0)
            
            # Create a temporary file for the fdisk commands
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                # Create a new DOS partition table
                f.write("o\n")
                
                # Create the FAT partition
                f.write("n\n")  # New partition
                f.write("p\n")  # Primary partition
                f.write("1\n")  # Partition number 1
                f.write("\n")   # Default first sector
                f.write(f"+{fat_size}M\n")  # Size in MiB
                f.write("t\n")  # Change partition type
                f.write("c\n")  # W95 FAT32 (LBA)
                f.write("a\n")  # Set bootable flag
                
                # Create the system partition
                f.write("n\n")  # New partition
                f.write("p\n")  # Primary partition
                f.write("2\n")  # Partition number 2
                f.write("\n")   # Default first sector
                f.write(f"+{system_size}G\n")  # Size in GiB
                
                # Create the home partition
                f.write("n\n")  # New partition
                f.write("p\n")  # Primary partition
                f.write("3\n")  # Partition number 3
                f.write("\n")   # Default first sector
                if home_size > 0:
                    f.write(f"+{home_size}G\n")  # Size in GiB
                else:
                    f.write("\n")  # Use all remaining space
                
                # Write the changes
                f.write("w\n")
                
                f.flush()
                
                # Run fdisk
                returncode, stdout, stderr = self.env_manager.run_command(
                    ['fdisk', device],
                    cwd=None,
                    stdin=open(f.name, 'r')
                )
                
                if returncode != 0:
                    logger.error("Failed to partition device: %s", stderr)
                    return False
            
            # Remove the temporary file
            os.unlink(f.name)
            
            logger.info("Device partitioned successfully")
            return True
        except Exception as e:
            logger.error("Error partitioning device: %s", str(e))
            return False
    
    def format_partitions(self, device: str) -> bool:
        """
        Format the partitions
        
        Args:
            device: Device to format (e.g., /dev/mmcblk1)
        
        Returns:
            True if the partitions were formatted successfully, False otherwise
        """
        try:
            logger.info("Formatting partitions on device: %s", device)
            
            # Get filesystem options
            filesystem = self.partition_config.get('filesystem', {})
            fat_type = filesystem.get('fat_type', 'vfat')
            system_type = filesystem.get('system_type', 'ext4')
            home_type = filesystem.get('home_type', 'ext4')
            
            # Format the FAT partition
            logger.info("Formatting FAT partition...")
            returncode, stdout, stderr = self.env_manager.run_command(
                ['mkfs.vfat', f"{device}p1"],
                cwd=None
            )
            
            if returncode != 0:
                logger.error("Failed to format FAT partition: %s", stderr)
                return False
            
            # Format the system partition
            logger.info("Formatting system partition...")
            
            # Get ext4 parameters
            ext4_params = filesystem.get('ext4_params', {})
            journal_size = ext4_params.get('journal_size', 4)
            block_size = ext4_params.get('block_size', 1024)
            inode_size = ext4_params.get('inode_size', 128)
            inode_ratio = ext4_params.get('inode_ratio', 4096)
            
            # Build the mkfs.ext4 command
            ext4_cmd = [
                'mkfs.ext4',
                '-O', '^64bit',
                '-O', '^metadata_csum',
                '-O', 'uninit_bg',
                '-J', f'size={journal_size}',
                '-b', str(block_size),
                '-i', str(inode_ratio),
                '-I', str(inode_size),
                f"{device}p2"
            ]
            
            returncode, stdout, stderr = self.env_manager.run_command(
                ext4_cmd,
                cwd=None
            )
            
            if returncode != 0:
                logger.error("Failed to format system partition: %s", stderr)
                return False
            
            # Format the home partition
            logger.info("Formatting home partition...")
            
            # Build the mkfs.ext4 command
            ext4_cmd = [
                'mkfs.ext4',
                '-O', '^64bit',
                '-O', '^metadata_csum',
                '-O', 'uninit_bg',
                '-J', f'size={journal_size}',
                '-b', str(block_size),
                '-i', str(inode_ratio),
                '-I', str(inode_size),
                f"{device}p3"
            ]
            
            returncode, stdout, stderr = self.env_manager.run_command(
                ext4_cmd,
                cwd=None
            )
            
            if returncode != 0:
                logger.error("Failed to format home partition: %s", stderr)
                return False
            
            logger.info("Partitions formatted successfully")
            return True
        except Exception as e:
            logger.error("Error formatting partitions: %s", str(e))
            return False
    
    def install_bootloader(self, device: str, bootloader_path: str) -> bool:
        """
        Install the bootloader to the device
        
        Args:
            device: Device to install the bootloader to (e.g., /dev/mmcblk1)
            bootloader_path: Path to the bootloader binary
        
        Returns:
            True if the bootloader was installed successfully, False otherwise
        """
        try:
            logger.info("Installing bootloader to device: %s", device)
            
            # Enable writing to the boot0 partition
            returncode, stdout, stderr = self.env_manager.run_command(
                ['sh', '-c', f'echo 0 > /sys/block/{os.path.basename(device)}boot0/force_ro'],
                cwd=None
            )
            
            if returncode != 0:
                logger.error("Failed to enable writing to boot0 partition: %s", stderr)
                return False
            
            # Zero out the boot0 partition
            returncode, stdout, stderr = self.env_manager.run_command(
                ['dd', 'if=/dev/zero', f'of={device}boot0', 'bs=512', 'count=4096'],
                cwd=None
            )
            
            if returncode != 0:
                logger.error("Failed to zero out boot0 partition: %s", stderr)
                return False
            
            # Install the bootloader
            returncode, stdout, stderr = self.env_manager.run_command(
                ['dd', f'if={bootloader_path}', f'of={device}boot0', 'bs=512', 'seek=2'],
                cwd=None
            )
            
            if returncode != 0:
                logger.error("Failed to install bootloader: %s", stderr)
                return False
            
            # Re-enable read-only mode for the boot0 partition
            returncode, stdout, stderr = self.env_manager.run_command(
                ['sh', '-c', f'echo 1 > /sys/block/{os.path.basename(device)}boot0/force_ro'],
                cwd=None
            )
            
            if returncode != 0:
                logger.error("Failed to re-enable read-only mode for boot0 partition: %s", stderr)
                return False
            
            logger.info("Bootloader installed successfully")
            return True
        except Exception as e:
            logger.error("Error installing bootloader: %s", str(e))
            return False
    
    def mount_partitions(self, device: str, mount_points: Dict[str, str]) -> bool:
        """
        Mount the partitions
        
        Args:
            device: Device to mount (e.g., /dev/mmcblk1)
            mount_points: Dictionary of partition numbers to mount points
        
        Returns:
            True if the partitions were mounted successfully, False otherwise
        """
        try:
            logger.info("Mounting partitions on device: %s", device)
            
            for partition, mount_point in mount_points.items():
                # Create the mount point if it doesn't exist
                os.makedirs(mount_point, exist_ok=True)
                
                # Mount the partition
                returncode, stdout, stderr = self.env_manager.run_command(
                    ['mount', f"{device}p{partition}", mount_point],
                    cwd=None
                )
                
                if returncode != 0:
                    logger.error("Failed to mount partition %s: %s", partition, stderr)
                    return False
                
                logger.info("Mounted partition %s to %s", partition, mount_point)
            
            logger.info("Partitions mounted successfully")
            return True
        except Exception as e:
            logger.error("Error mounting partitions: %s", str(e))
            return False
    
    def unmount_partitions(self, mount_points: List[str]) -> bool:
        """
        Unmount the partitions
        
        Args:
            mount_points: List of mount points to unmount
        
        Returns:
            True if the partitions were unmounted successfully, False otherwise
        """
        try:
            logger.info("Unmounting partitions...")
            
            for mount_point in mount_points:
                # Unmount the partition
                returncode, stdout, stderr = self.env_manager.run_command(
                    ['umount', mount_point],
                    cwd=None
                )
                
                if returncode != 0:
                    logger.error("Failed to unmount %s: %s", mount_point, stderr)
                    return False
                
                logger.info("Unmounted %s", mount_point)
            
            logger.info("Partitions unmounted successfully")
            return True
        except Exception as e:
            logger.error("Error unmounting partitions: %s", str(e))
            return False