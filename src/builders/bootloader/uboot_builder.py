#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
U-Boot Bootloader Builder for Parabola RM

This module handles the compilation and configuration of the U-Boot bootloader.
"""

import os
import sys
import logging
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Tuple

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.cross_env.env_manager import CrossEnvManager

logger = logging.getLogger(__name__)

class UBootBuilder:
    """
    U-Boot Bootloader Builder
    
    This class is responsible for compiling and configuring the U-Boot bootloader.
    """
    
    def __init__(self, config: Dict[str, Any], env_manager: CrossEnvManager):
        """
        Initialize the U-Boot Bootloader Builder
        
        Args:
            config: Configuration dictionary
            env_manager: Cross-compilation environment manager
        """
        self.config = config
        self.env_manager = env_manager
        self.bootloader_config = config.get('bootloader', {})
        
        # Set up paths
        self.build_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'build',
            'bootloader'
        )
        
        # Create build directory if it doesn't exist
        os.makedirs(self.build_dir, exist_ok=True)
    
    def build(self) -> bool:
        """
        Build the U-Boot bootloader
        
        Returns:
            True if the bootloader was built successfully, False otherwise
        """
        try:
            # Clone the U-Boot repository
            if not self._clone_uboot():
                return False
            
            # Apply patches
            if not self._apply_patches():
                return False
            
            # Configure U-Boot
            if not self._configure_uboot():
                return False
            
            # Build U-Boot
            if not self._build_uboot():
                return False
            
            logger.info("U-Boot bootloader built successfully")
            return True
        except Exception as e:
            logger.error("Error building U-Boot bootloader: %s", str(e))
            return False
    
    def _clone_uboot(self) -> bool:
        """
        Clone the U-Boot repository
        
        Returns:
            True if the repository was cloned successfully, False otherwise
        """
        try:
            # Check if the repository already exists
            uboot_dir = os.path.join(self.build_dir, 'uboot')
            
            if os.path.isdir(uboot_dir):
                logger.info("U-Boot repository already exists, updating...")
                
                # Update the repository
                returncode, stdout, stderr = self.env_manager.run_command(
                    ['git', 'pull'],
                    cwd=uboot_dir
                )
                
                if returncode != 0:
                    logger.error("Failed to update U-Boot repository: %s", stderr)
                    return False
            else:
                logger.info("Cloning U-Boot repository...")
                
                # Clone the repository
                returncode, stdout, stderr = self.env_manager.run_command(
                    [
                        'git',
                        'clone',
                        'https://github.com/remarkable/uboot.git',
                        uboot_dir
                    ]
                )
                
                if returncode != 0:
                    logger.error("Failed to clone U-Boot repository: %s", stderr)
                    return False
            
            logger.info("U-Boot repository cloned/updated successfully")
            return True
        except Exception as e:
            logger.error("Error cloning U-Boot repository: %s", str(e))
            return False
    
    def _apply_patches(self) -> bool:
        """
        Apply patches to the U-Boot source code
        
        Returns:
            True if the patches were applied successfully, False otherwise
        """
        try:
            # Check if there are any patches to apply
            patches_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'resources',
                'patches',
                'bootloader'
            )
            
            if not os.path.isdir(patches_dir) or not os.listdir(patches_dir):
                logger.info("No patches to apply")
                return True
            
            # Apply patches
            uboot_dir = os.path.join(self.build_dir, 'uboot')
            
            for patch_file in sorted(os.listdir(patches_dir)):
                if not patch_file.endswith('.patch'):
                    continue
                
                logger.info("Applying patch: %s", patch_file)
                
                patch_path = os.path.join(patches_dir, patch_file)
                
                returncode, stdout, stderr = self.env_manager.run_command(
                    ['git', 'apply', patch_path],
                    cwd=uboot_dir
                )
                
                if returncode != 0:
                    logger.error("Failed to apply patch %s: %s", patch_file, stderr)
                    return False
            
            logger.info("Patches applied successfully")
            return True
        except Exception as e:
            logger.error("Error applying patches: %s", str(e))
            return False
    
    def _configure_uboot(self) -> bool:
        """
        Configure U-Boot
        
        Returns:
            True if U-Boot was configured successfully, False otherwise
        """
        try:
            # Configure U-Boot
            uboot_dir = os.path.join(self.build_dir, 'uboot')
            
            logger.info("Configuring U-Boot...")
            
            # Set up environment variables
            env_vars = {
                'ARCH': 'arm',
                'CROSS_COMPILE': 'arm-poky-linux-gnueabi-'
            }
            
            # Make the zero-gravitas_defconfig
            returncode, stdout, stderr = self.env_manager.run_command(
                ['make', 'zero-gravitas_defconfig'],
                cwd=uboot_dir
            )
            
            if returncode != 0:
                logger.error("Failed to configure U-Boot: %s", stderr)
                return False
            
            # Modify the configuration based on user settings
            self._modify_uboot_config(uboot_dir)
            
            logger.info("U-Boot configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring U-Boot: %s", str(e))
            return False
    
    def _modify_uboot_config(self, uboot_dir: str) -> None:
        """
        Modify the U-Boot configuration based on user settings
        
        Args:
            uboot_dir: Path to the U-Boot directory
        """
        # Modify include/configs/zero-gravitas.h
        config_file = os.path.join(uboot_dir, 'include', 'configs', 'zero-gravitas.h')
        
        if not os.path.isfile(config_file):
            logger.warning("U-Boot configuration file not found: %s", config_file)
            return
        
        # Read the configuration file
        with open(config_file, 'r') as f:
            config_content = f.read()
        
        # Modify the configuration
        boot_params = self.bootloader_config.get('boot_params', {})
        
        # Replace the mmcargs line
        mmcargs = f'"mmcargs=setenv bootargs console=${{{boot_params.get('console', 'console')}}},{boot_params.get('baudrate', '${baudrate}')} " \\\n'
        mmcargs += f'                       "root={boot_params.get('root_device', '/dev/mmcblk1p2')} {boot_params.get('additional_params', 'rootwait rootfstype=ext4 rw')} por=${{{boot_params.get('por', 'por')}}};"\\0" \\\n'
        
        # Replace the mmcargs line in the configuration
        import re
        config_content = re.sub(
            r'"mmcargs=setenv bootargs.*?\\0" \\',
            mmcargs,
            config_content,
            flags=re.DOTALL
        )
        
        # Write the modified configuration
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        logger.debug("U-Boot configuration modified successfully")
    
    def _build_uboot(self) -> bool:
        """
        Build U-Boot
        
        Returns:
            True if U-Boot was built successfully, False otherwise
        """
        try:
            # Build U-Boot
            uboot_dir = os.path.join(self.build_dir, 'uboot')
            
            logger.info("Building U-Boot...")
            
            # Set up environment variables
            env_vars = {
                'ARCH': 'arm',
                'CROSS_COMPILE': 'arm-poky-linux-gnueabi-'
            }
            
            # Build U-Boot
            returncode, stdout, stderr = self.env_manager.run_command(
                ['make', '-j', str(self.config.get('cross_compilation', {}).get('build', {}).get('parallel_jobs', 4))],
                cwd=uboot_dir
            )
            
            if returncode != 0:
                logger.error("Failed to build U-Boot: %s", stderr)
                return False
            
            # Copy the U-Boot binary to the output directory
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'output',
                'bootloader'
            )
            
            os.makedirs(output_dir, exist_ok=True)
            
            shutil.copy(
                os.path.join(uboot_dir, 'u-boot.imx'),
                os.path.join(output_dir, 'u-boot.imx')
            )
            
            logger.info("U-Boot built successfully")
            return True
        except Exception as e:
            logger.error("Error building U-Boot: %s", str(e))
            return False
    
    def get_output_path(self) -> str:
        """
        Get the path to the built U-Boot binary
        
        Returns:
            Path to the U-Boot binary
        """
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'output',
            'bootloader',
            'u-boot.imx'
        )