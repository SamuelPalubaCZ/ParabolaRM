#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Linux Kernel Builder for Parabola RM

This module handles the compilation and configuration of the Linux kernel.
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

class KernelBuilder:
    """
    Linux Kernel Builder
    
    This class is responsible for compiling and configuring the Linux kernel.
    """
    
    def __init__(self, config: Dict[str, Any], env_manager: CrossEnvManager):
        """
        Initialize the Linux Kernel Builder
        
        Args:
            config: Configuration dictionary
            env_manager: Cross-compilation environment manager
        """
        self.config = config
        self.env_manager = env_manager
        self.kernel_config = config.get('kernel', {})
        
        # Set up paths
        self.build_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'build',
            'kernel'
        )
        
        # Create build directory if it doesn't exist
        os.makedirs(self.build_dir, exist_ok=True)
    
    def build(self) -> bool:
        """
        Build the Linux kernel
        
        Returns:
            True if the kernel was built successfully, False otherwise
        """
        try:
            # Clone the kernel repository
            if not self._clone_kernel():
                return False
            
            # Apply patches
            if not self._apply_patches():
                return False
            
            # Remove proprietary blobs
            if not self._remove_proprietary_blobs():
                return False
            
            # Configure kernel
            if not self._configure_kernel():
                return False
            
            # Build kernel
            if not self._build_kernel():
                return False
            
            logger.info("Linux kernel built successfully")
            return True
        except Exception as e:
            logger.error("Error building Linux kernel: %s", str(e))
            return False
    
    def _clone_kernel(self) -> bool:
        """
        Clone the Linux kernel repository
        
        Returns:
            True if the repository was cloned successfully, False otherwise
        """
        try:
            # Check if the repository already exists
            kernel_dir = os.path.join(self.build_dir, 'linux')
            
            if os.path.isdir(kernel_dir):
                logger.info("Linux kernel repository already exists, updating...")
                
                # Update the repository
                returncode, stdout, stderr = self.env_manager.run_command(
                    ['git', 'pull'],
                    cwd=kernel_dir
                )
                
                if returncode != 0:
                    logger.error("Failed to update Linux kernel repository: %s", stderr)
                    return False
            else:
                logger.info("Cloning Linux kernel repository...")
                
                # Clone the repository
                returncode, stdout, stderr = self.env_manager.run_command(
                    [
                        'git',
                        'clone',
                        '--branch',
                        'lars/zero-gravitas_4.9',
                        'https://github.com/remarkable/linux.git',
                        kernel_dir
                    ]
                )
                
                if returncode != 0:
                    logger.error("Failed to clone Linux kernel repository: %s", stderr)
                    return False
            
            logger.info("Linux kernel repository cloned/updated successfully")
            return True
        except Exception as e:
            logger.error("Error cloning Linux kernel repository: %s", str(e))
            return False
    
    def _apply_patches(self) -> bool:
        """
        Apply patches to the Linux kernel source code
        
        Returns:
            True if the patches were applied successfully, False otherwise
        """
        try:
            # Check if there are any patches to apply
            patches_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'resources',
                'patches',
                'kernel'
            )
            
            if not os.path.isdir(patches_dir) or not os.listdir(patches_dir):
                logger.info("No patches to apply")
                return True
            
            # Apply patches
            kernel_dir = os.path.join(self.build_dir, 'linux')
            
            for patch_file in sorted(os.listdir(patches_dir)):
                if not patch_file.endswith('.patch'):
                    continue
                
                logger.info("Applying patch: %s", patch_file)
                
                patch_path = os.path.join(patches_dir, patch_file)
                
                returncode, stdout, stderr = self.env_manager.run_command(
                    ['git', 'apply', patch_path],
                    cwd=kernel_dir
                )
                
                if returncode != 0:
                    logger.error("Failed to apply patch %s: %s", patch_file, stderr)
                    return False
            
            logger.info("Patches applied successfully")
            return True
        except Exception as e:
            logger.error("Error applying patches: %s", str(e))
            return False
    
    def _remove_proprietary_blobs(self) -> bool:
        """
        Remove proprietary blobs from the Linux kernel
        
        Returns:
            True if the blobs were removed successfully, False otherwise
        """
        try:
            kernel_dir = os.path.join(self.build_dir, 'linux')
            
            logger.info("Removing proprietary blobs from the Linux kernel...")
            
            # Remove all firmware files except for the EPDC waveform file
            firmware_dir = os.path.join(kernel_dir, 'firmware')
            
            if os.path.isdir(firmware_dir):
                for root, dirs, files in os.walk(firmware_dir):
                    for file in files:
                        if file != 'epdc_ES103CS1.fw.ihex':
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
                            logger.debug("Removed proprietary blob: %s", file_path)
            
            logger.info("Proprietary blobs removed successfully")
            return True
        except Exception as e:
            logger.error("Error removing proprietary blobs: %s", str(e))
            return False
    
    def _configure_kernel(self) -> bool:
        """
        Configure the Linux kernel
        
        Returns:
            True if the kernel was configured successfully, False otherwise
        """
        try:
            kernel_dir = os.path.join(self.build_dir, 'linux')
            
            logger.info("Configuring Linux kernel...")
            
            # Set up environment variables
            env_vars = {
                'ARCH': 'arm',
                'CROSS_COMPILE': 'arm-poky-linux-gnueabi-'
            }
            
            # Make the zero-gravitas_defconfig
            returncode, stdout, stderr = self.env_manager.run_command(
                ['make', 'zero-gravitas_defconfig'],
                cwd=kernel_dir
            )
            
            if returncode != 0:
                logger.error("Failed to configure Linux kernel: %s", stderr)
                return False
            
            # Modify the configuration based on user settings
            self._modify_kernel_config(kernel_dir)
            
            logger.info("Linux kernel configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring Linux kernel: %s", str(e))
            return False
    
    def _modify_kernel_config(self, kernel_dir: str) -> None:
        """
        Modify the Linux kernel configuration based on user settings
        
        Args:
            kernel_dir: Path to the Linux kernel directory
        """
        # Modify arch/arm/configs/zero-gravitas_defconfig
        config_file = os.path.join(kernel_dir, 'arch', 'arm', 'configs', 'zero-gravitas_defconfig')
        
        if not os.path.isfile(config_file):
            logger.warning("Linux kernel configuration file not found: %s", config_file)
            return
        
        # Read the configuration file
        with open(config_file, 'r') as f:
            config_content = f.read()
        
        # Modify the configuration
        drivers = self.kernel_config.get('drivers', {})
        
        # EPDC driver settings
        epdc = drivers.get('epdc', {})
        if epdc.get('auto_partial_refresh', True):
            config_content = self._ensure_config_option(config_content, 'CONFIG_FB_MXC_EINK_AUTO_UPDATE_MODE', 'y')
        else:
            config_content = self._ensure_config_option(config_content, 'CONFIG_FB_MXC_EINK_AUTO_UPDATE_MODE', 'n')
        
        # USB communication options
        usb = drivers.get('usb', {})
        if usb.get('enable_acm', True):
            config_content = self._ensure_config_option(config_content, 'CONFIG_USB_ACM', 'y')
            config_content = self._ensure_config_option(config_content, 'CONFIG_USB_F_ACM', 'y')
        else:
            config_content = self._ensure_config_option(config_content, 'CONFIG_USB_ACM', 'n')
            config_content = self._ensure_config_option(config_content, 'CONFIG_USB_F_ACM', 'n')
        
        if usb.get('enable_cdc_composite', True):
            config_content = self._ensure_config_option(config_content, 'CONFIG_USB_U_SERIAL', 'y')
            config_content = self._ensure_config_option(config_content, 'CONFIG_USB_CDC_COMPOSITE', 'y')
        else:
            config_content = self._ensure_config_option(config_content, 'CONFIG_USB_U_SERIAL', 'n')
            config_content = self._ensure_config_option(config_content, 'CONFIG_USB_CDC_COMPOSITE', 'n')
        
        # Hardware support
        hardware_support = self.kernel_config.get('hardware_support', {})
        
        # Wi-Fi support
        if hardware_support.get('wifi_support', False):
            config_content = self._ensure_config_option(config_content, 'CONFIG_BRCMFMAC', 'm')
        else:
            config_content = self._ensure_config_option(config_content, 'CONFIG_BRCMFMAC', 'n')
        
        # Power management
        if hardware_support.get('power_management', True):
            config_content = self._ensure_config_option(config_content, 'CONFIG_PM', 'y')
            config_content = self._ensure_config_option(config_content, 'CONFIG_PM_SLEEP', 'y')
        else:
            config_content = self._ensure_config_option(config_content, 'CONFIG_PM', 'n')
            config_content = self._ensure_config_option(config_content, 'CONFIG_PM_SLEEP', 'n')
        
        # Write the modified configuration
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        logger.debug("Linux kernel configuration modified successfully")
    
    def _ensure_config_option(self, config_content: str, option: str, value: str) -> str:
        """
        Ensure that a configuration option is set to the specified value
        
        Args:
            config_content: Configuration file content
            option: Configuration option
            value: Value to set
        
        Returns:
            Modified configuration file content
        """
        # Check if the option exists
        if re.search(rf'^{option}=', config_content, re.MULTILINE):
            # Replace the existing option
            config_content = re.sub(
                rf'^{option}=.*$',
                f'{option}={value}',
                config_content,
                flags=re.MULTILINE
            )
        else:
            # Add the option
            config_content += f'\n{option}={value}\n'
        
        return config_content
    
    def _build_kernel(self) -> bool:
        """
        Build the Linux kernel
        
        Returns:
            True if the kernel was built successfully, False otherwise
        """
        try:
            kernel_dir = os.path.join(self.build_dir, 'linux')
            
            logger.info("Building Linux kernel...")
            
            # Set up environment variables
            env_vars = {
                'ARCH': 'arm',
                'CROSS_COMPILE': 'arm-poky-linux-gnueabi-'
            }
            
            # Build the kernel
            returncode, stdout, stderr = self.env_manager.run_command(
                ['make', '-j', str(self.config.get('cross_compilation', {}).get('build', {}).get('parallel_jobs', 4))],
                cwd=kernel_dir
            )
            
            if returncode != 0:
                logger.error("Failed to build Linux kernel: %s", stderr)
                return False
            
            # Create the output directory
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'output',
                'kernel'
            )
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Copy the kernel image and device tree binary
            shutil.copy(
                os.path.join(kernel_dir, 'arch', 'arm', 'boot', 'zImage'),
                os.path.join(output_dir, 'zImage')
            )
            
            shutil.copy(
                os.path.join(kernel_dir, 'arch', 'arm', 'boot', 'dts', 'zero-gravitas.dtb'),
                os.path.join(output_dir, 'zero-gravitas.dtb')
            )
            
            # Copy the EPDC waveform file
            shutil.copy(
                os.path.join(kernel_dir, 'firmware', 'epdc_ES103CS1.fw.ihex'),
                os.path.join(output_dir, 'epdc_ES103CS1.fw.ihex')
            )
            
            logger.info("Linux kernel built successfully")
            return True
        except Exception as e:
            logger.error("Error building Linux kernel: %s", str(e))
            return False
    
    def get_output_paths(self) -> Dict[str, str]:
        """
        Get the paths to the built kernel files
        
        Returns:
            Dictionary of file names to paths
        """
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'output',
            'kernel'
        )
        
        return {
            'zImage': os.path.join(output_dir, 'zImage'),
            'dtb': os.path.join(output_dir, 'zero-gravitas.dtb'),
            'waveform': os.path.join(output_dir, 'epdc_ES103CS1.fw.ihex')
        }