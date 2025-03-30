#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System Installer for Parabola RM

This module handles the installation of the Parabola system files.
"""

import os
import sys
import logging
import tempfile
import shutil
import re
import urllib.request
import tarfile
from typing import Dict, Any, List, Optional, Tuple

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.cross_env.env_manager import CrossEnvManager

logger = logging.getLogger(__name__)

class SystemInstaller:
    """
    System Installer
    
    This class is responsible for installing the Parabola system files.
    """
    
    def __init__(self, config: Dict[str, Any], env_manager: CrossEnvManager):
        """
        Initialize the System Installer
        
        Args:
            config: Configuration dictionary
            env_manager: Cross-compilation environment manager
        """
        self.config = config
        self.env_manager = env_manager
        self.system_config = config.get('system', {})
        
        # Set up paths
        self.build_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'build',
            'system'
        )
        
        # Create build directory if it doesn't exist
        os.makedirs(self.build_dir, exist_ok=True)
    
    def install(self, mount_points: Dict[str, str], kernel_files: Dict[str, str], bootloader_files: Dict[str, str]) -> bool:
        """
        Install the Parabola system files
        
        Args:
            mount_points: Dictionary of partition numbers to mount points
            kernel_files: Dictionary of kernel file names to paths
            bootloader_files: Dictionary of bootloader file names to paths
        
        Returns:
            True if the system was installed successfully, False otherwise
        """
        try:
            # Download the Parabola rootfs
            if not self._download_rootfs():
                return False
            
            # Extract the rootfs
            if not self._extract_rootfs(mount_points[2]):
                return False
            
            # Install the kernel
            if not self._install_kernel(mount_points[2], kernel_files):
                return False
            
            # Install the bootloader files
            if not self._install_bootloader_files(mount_points[1], bootloader_files):
                return False
            
            # Configure the system
            if not self._configure_system(mount_points[2]):
                return False
            
            logger.info("Parabola system installed successfully")
            return True
        except Exception as e:
            logger.error("Error installing Parabola system: %s", str(e))
            return False
    
    def _download_rootfs(self) -> bool:
        """
        Download the Parabola rootfs
        
        Returns:
            True if the rootfs was downloaded successfully, False otherwise
        """
        try:
            rootfs_path = os.path.join(self.build_dir, 'parabola-rootfs.tar.gz')
            
            # Check if the rootfs already exists
            if os.path.isfile(rootfs_path):
                logger.info("Parabola rootfs already downloaded")
                return True
            
            logger.info("Downloading Parabola rootfs...")
            
            # Download the rootfs
            rootfs_url = "https://repo.parabola.nu/iso/armv7h/parabola-systemd-cli-armv7h-latest.tar.gz"
            
            urllib.request.urlretrieve(rootfs_url, rootfs_path)
            
            logger.info("Parabola rootfs downloaded successfully")
            return True
        except Exception as e:
            logger.error("Error downloading Parabola rootfs: %s", str(e))
            return False
    
    def _extract_rootfs(self, mount_point: str) -> bool:
        """
        Extract the Parabola rootfs
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if the rootfs was extracted successfully, False otherwise
        """
        try:
            rootfs_path = os.path.join(self.build_dir, 'parabola-rootfs.tar.gz')
            
            logger.info("Extracting Parabola rootfs...")
            
            # Extract the rootfs
            with tarfile.open(rootfs_path, 'r:gz') as tar:
                tar.extractall(path=mount_point)
            
            logger.info("Parabola rootfs extracted successfully")
            return True
        except Exception as e:
            logger.error("Error extracting Parabola rootfs: %s", str(e))
            return False
    
    def _install_kernel(self, mount_point: str, kernel_files: Dict[str, str]) -> bool:
        """
        Install the kernel files
        
        Args:
            mount_point: Mount point for the system partition
            kernel_files: Dictionary of kernel file names to paths
        
        Returns:
            True if the kernel was installed successfully, False otherwise
        """
        try:
            logger.info("Installing kernel files...")
            
            # Create the boot directory
            boot_dir = os.path.join(mount_point, 'boot')
            os.makedirs(boot_dir, exist_ok=True)
            
            # Copy the kernel image
            shutil.copy(kernel_files['zImage'], os.path.join(boot_dir, 'zImage'))
            
            # Copy the device tree binary
            shutil.copy(kernel_files['dtb'], os.path.join(boot_dir, 'zero-gravitas.dtb'))
            
            logger.info("Kernel files installed successfully")
            return True
        except Exception as e:
            logger.error("Error installing kernel files: %s", str(e))
            return False
    
    def _install_bootloader_files(self, mount_point: str, bootloader_files: Dict[str, str]) -> bool:
        """
        Install the bootloader files
        
        Args:
            mount_point: Mount point for the FAT partition
            bootloader_files: Dictionary of bootloader file names to paths
        
        Returns:
            True if the bootloader files were installed successfully, False otherwise
        """
        try:
            logger.info("Installing bootloader files...")
            
            # Copy the waveform file
            if 'waveform' in bootloader_files:
                shutil.copy(bootloader_files['waveform'], os.path.join(mount_point, 'waveform.bin'))
            
            # Copy the splash screen
            if 'splash' in bootloader_files:
                shutil.copy(bootloader_files['splash'], os.path.join(mount_point, 'splash.bmp'))
            
            logger.info("Bootloader files installed successfully")
            return True
        except Exception as e:
            logger.error("Error installing bootloader files: %s", str(e))
            return False
    
    def _configure_system(self, mount_point: str) -> bool:
        """
        Configure the system
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if the system was configured successfully, False otherwise
        """
        try:
            logger.info("Configuring system...")
            
            # Configure fstab
            if not self._configure_fstab(mount_point):
                return False
            
            # Configure network
            if not self._configure_network(mount_point):
                return False
            
            # Configure serial console
            if not self._configure_serial_console(mount_point):
                return False
            
            # Configure PAM
            if not self._configure_pam(mount_point):
                return False
            
            logger.info("System configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring system: %s", str(e))
            return False
    
    def _configure_fstab(self, mount_point: str) -> bool:
        """
        Configure the fstab file
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if fstab was configured successfully, False otherwise
        """
        try:
            fstab_path = os.path.join(mount_point, 'etc', 'fstab')
            
            logger.info("Configuring fstab...")
            
            # Write the fstab file
            with open(fstab_path, 'w') as f:
                f.write("/dev/mmcblk1p2  /               auto    defaults                    1  1\n")
                f.write("/dev/mmcblk1p1  /var/lib/uboot  auto    defaults                    0  0\n")
                f.write("/dev/mmcblk1p3  /home           auto    defaults                    0  2\n")
                f.write("devpts  /dev/pts        devpts  mode=0620,gid=5                     0  0\n")
                f.write("proc    /proc           proc    defaults                            0  0\n")
                f.write("tmpfs   /run            tmpfs   mode=0755,nodev,nosuid,strictatime  0  0\n")
                f.write("tmpfs   /tmp            tmpfs   defaults                            0  0\n")
                f.write("tmpfs   /root/.cache    tmpfs   defaults,size=20M                   0  0\n")
            
            logger.info("fstab configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring fstab: %s", str(e))
            return False
    
    def _configure_network(self, mount_point: str) -> bool:
        """
        Configure the network
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if the network was configured successfully, False otherwise
        """
        try:
            network_dir = os.path.join(mount_point, 'etc', 'systemd', 'network')
            
            logger.info("Configuring network...")
            
            # Create the network directory if it doesn't exist
            os.makedirs(network_dir, exist_ok=True)
            
            # Configure USB networking
            usb_networking = self.system_config.get('network', {}).get('usb_networking', {})
            
            if usb_networking.get('enable', True):
                # Write the USB network configuration
                usb0_path = os.path.join(network_dir, 'usb0.network')
                
                with open(usb0_path, 'w') as f:
                    f.write("[Match]\n")
                    f.write("Name=usb0\n\n")
                    f.write("[Network]\n")
                    f.write(f"Address={usb_networking.get('ip_address', '10.11.99.1')}/{usb_networking.get('netmask', '255.255.255.0').count('255')}\n")
            
            # Configure DHCP server
            dhcp_server = self.system_config.get('network', {}).get('dhcp_server', {})
            
            if dhcp_server.get('enable', True):
                # Install dnsmasq configuration
                dnsmasq_path = os.path.join(mount_point, 'etc', 'dnsmasq.conf')
                
                with open(dnsmasq_path, 'w') as f:
                    f.write("interface=usb0\n")
                    f.write("bind-interfaces\n")
                    f.write(f"dhcp-range={dhcp_server.get('range_start', '10.11.99.2')},{dhcp_server.get('range_end', '10.11.99.253')},{dhcp_server.get('lease_time', 10)}m\n")
                    f.write("dhcp-option=6  # Don't send DNS\n")
            
            logger.info("Network configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring network: %s", str(e))
            return False
    
    def _configure_serial_console(self, mount_point: str) -> bool:
        """
        Configure the serial console
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if the serial console was configured successfully, False otherwise
        """
        try:
            getty_dir = os.path.join(mount_point, 'etc', 'systemd', 'system', 'getty.target.wants')
            
            logger.info("Configuring serial console...")
            
            # Create the getty directory if it doesn't exist
            os.makedirs(getty_dir, exist_ok=True)
            
            # Create a symlink for the serial console
            serial_getty_path = os.path.join(getty_dir, 'serial-getty@ttyGS0.service')
            serial_getty_target = '/usr/lib/systemd/system/serial-getty@.service'
            
            # Create the symlink
            if not os.path.exists(serial_getty_path):
                os.symlink(serial_getty_target, serial_getty_path)
            
            logger.info("Serial console configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring serial console: %s", str(e))
            return False
    
    def _configure_pam(self, mount_point: str) -> bool:
        """
        Configure PAM
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if PAM was configured successfully, False otherwise
        """
        try:
            pam_login_path = os.path.join(mount_point, 'etc', 'pam.d', 'login')
            pam_system_login_path = os.path.join(mount_point, 'etc', 'pam.d', 'system-login')
            
            logger.info("Configuring PAM...")
            
            # Disable pam_securetty.so in login
            if os.path.isfile(pam_login_path):
                with open(pam_login_path, 'r') as f:
                    content = f.read()
                
                content = content.replace('auth       required     pam_securetty.so', '#auth       required     pam_securetty.so')
                
                with open(pam_login_path, 'w') as f:
                    f.write(content)
            
            # Disable pam_systemd.so in system-login
            if os.path.isfile(pam_system_login_path):
                with open(pam_system_login_path, 'r') as f:
                    content = f.read()
                
                content = content.replace('session   optional   pam_systemd.so', '#-session   optional   pam_systemd.so')
                
                with open(pam_system_login_path, 'w') as f:
                    f.write(content)
            
            logger.info("PAM configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring PAM: %s", str(e))
            return False
    
    def configure_auto_login(self, mount_point: str) -> bool:
        """
        Configure automatic login
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if automatic login was configured successfully, False otherwise
        """
        try:
            getty_service_path = os.path.join(mount_point, 'etc', 'systemd', 'system', 'getty.target.wants', 'getty@tty1.service')
            
            logger.info("Configuring automatic login...")
            
            # Check if the getty service exists
            if not os.path.isfile(getty_service_path):
                logger.warning("Getty service not found: %s", getty_service_path)
                return False
            
            # Read the service file
            with open(getty_service_path, 'r') as f:
                content = f.read()
            
            # Modify the ExecStart line to auto-login as root
            content = re.sub(
                r'ExecStart=-/sbin/agetty.*',
                'ExecStart=-/sbin/agetty -a root --noclear %I $TERM',
                content
            )
            
            # Write the modified service file
            with open(getty_service_path, 'w') as f:
                f.write(content)
            
            logger.info("Automatic login configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring automatic login: %s", str(e))
            return False
    
    def configure_shutdown(self, mount_point: str) -> bool:
        """
        Configure graceful shutdown
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if graceful shutdown was configured successfully, False otherwise
        """
        try:
            shutdown_dir = os.path.join(mount_point, 'var', 'lib', 'remarkable')
            shutdown_script_path = os.path.join(shutdown_dir, 'shutdown.sh')
            shutdown_service_path = os.path.join(mount_point, 'etc', 'systemd', 'system', 'remarkable-shutdown.service')
            
            logger.info("Configuring graceful shutdown...")
            
            # Create the remarkable directory if it doesn't exist
            os.makedirs(shutdown_dir, exist_ok=True)
            
            # Write the shutdown script
            with open(shutdown_script_path, 'w') as f:
                f.write("#!/usr/bin/env bash\n")
                f.write("pgrep Xorg | xargs wait\n")
                f.write("sleep 1\n")
                f.write("journalctl --vacuum-size=100M\n")
                f.write("/var/lib/remarkable/epdc-show-bitmap /var/lib/uboot/splash-off.raw\n")
            
            # Make the script executable
            os.chmod(shutdown_script_path, 0o755)
            
            # Write the shutdown service
            with open(shutdown_service_path, 'w') as f:
                f.write("[Unit]\n")
                f.write("Description=rM shutdown helper\n\n")
                f.write("[Service]\n")
                f.write("Type=oneshot\n")
                f.write("RemainAfterExit=true\n")
                f.write("ExecStop=/var/lib/remarkable/shutdown.sh\n\n")
                f.write("[Install]\n")
                f.write("WantedBy=multi-user.target\n")
            
            logger.info("Graceful shutdown configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring graceful shutdown: %s", str(e))
            return False