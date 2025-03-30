#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Desktop Environment Configurator for Parabola RM

This module handles the installation and configuration of the desktop environment.
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

class DesktopConfigurator:
    """
    Desktop Environment Configurator
    
    This class is responsible for installing and configuring the desktop environment.
    """
    
    def __init__(self, config: Dict[str, Any], env_manager: CrossEnvManager):
        """
        Initialize the Desktop Environment Configurator
        
        Args:
            config: Configuration dictionary
            env_manager: Cross-compilation environment manager
        """
        self.config = config
        self.env_manager = env_manager
        self.desktop_config = config.get('desktop', {})
    
    def install(self, mount_point: str) -> bool:
        """
        Install and configure the desktop environment
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if the desktop environment was installed and configured successfully, False otherwise
        """
        try:
            # Get the desktop environment
            environment = self.desktop_config.get('environment', 'xfce')
            
            if environment == 'none':
                logger.info("No desktop environment selected, skipping installation")
                return True
            
            # Install Xorg
            if not self._install_xorg(mount_point):
                return False
            
            # Install the desktop environment
            if environment == 'xfce':
                if not self._install_xfce(mount_point):
                    return False
            else:
                logger.warning("Unsupported desktop environment: %s", environment)
                return False
            
            # Configure automatic loading
            if not self._configure_auto_loading(mount_point):
                return False
            
            # Configure e-paper optimizations
            if not self._configure_epaper_optimizations(mount_point):
                return False
            
            # Configure input methods
            if not self._configure_input_methods(mount_point):
                return False
            
            logger.info("Desktop environment installed and configured successfully")
            return True
        except Exception as e:
            logger.error("Error installing desktop environment: %s", str(e))
            return False
    
    def _install_xorg(self, mount_point: str) -> bool:
        """
        Install Xorg
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if Xorg was installed successfully, False otherwise
        """
        try:
            logger.info("Installing Xorg...")
            
            # Create a pacman command to install Xorg
            pacman_cmd = [
                'chroot',
                mount_point,
                'pacman',
                '-S',
                '--noconfirm',
                'xorg-server',
                'xf86-video-fbdev',
                'xf86-input-evdev'
            ]
            
            # Run the pacman command
            returncode, stdout, stderr = self.env_manager.run_command(
                pacman_cmd,
                cwd=None
            )
            
            if returncode != 0:
                logger.error("Failed to install Xorg: %s", stderr)
                return False
            
            # Create the Xorg configuration
            xorg_conf_dir = os.path.join(mount_point, 'etc', 'X11')
            os.makedirs(xorg_conf_dir, exist_ok=True)
            
            xorg_conf_path = os.path.join(xorg_conf_dir, 'xorg.conf')
            
            with open(xorg_conf_path, 'w') as f:
                f.write('Section "ServerLayout"\n')
                f.write('    Identifier     "Default Layout"\n')
                f.write('    Screen         0 "Screen0" 0 0\n')
                f.write('    InputDevice    "Wacom" "CorePointer"\n')
                f.write('    InputDevice    "Touchscreen" "CorePointer"\n')
                f.write('    InputDevice    "Keyboard0" "CoreKeyboard"\n')
                f.write('EndSection\n\n')
                
                f.write('Section "InputDevice"\n')
                f.write('    Identifier     "Keyboard0"\n')
                f.write('    Driver         "kbd"\n')
                f.write('    Option         "XkbLayout" "us"\n')
                f.write('EndSection\n\n')
                
                f.write('Section "InputDevice"\n')
                f.write('    Identifier     "Wacom"\n')
                f.write('    Driver         "evdev"\n')
                f.write('    Option         "Device" "/dev/input/event1"\n')
                f.write('    Option         "Name" "Wacom I2C Digitizer"\n')
                f.write('    Option         "Calibration" "0 20966 0 15725"\n')
                f.write('    Option         "InvertY" "true"\n')
                f.write('EndSection\n\n')
                
                f.write('Section "InputDevice"\n')
                f.write('    Identifier     "Touchscreen"\n')
                f.write('    Driver         "evdev"\n')
                f.write('    Option         "Device" "/dev/input/event2"\n')
                f.write('    Option         "Name" "cyttsp5_mt"\n')
                f.write('    Option         "Calibration" "0 20966 0 15725"\n')
                f.write('    Option         "InvertY" "true"\n')
                f.write('EndSection\n\n')
                
                f.write('Section "Device"\n')
                f.write('    Identifier     "Card0"\n')
                f.write('    Driver         "fbdev"\n')
                f.write('    Option         "fbdev" "/dev/fb0"\n')
                f.write('EndSection\n\n')
                
                f.write('Section "Screen"\n')
                f.write('    Identifier     "Screen0"\n')
                f.write('    Device         "Card0"\n')
                f.write('    DefaultDepth    16\n')
                f.write('EndSection\n')
            
            # Create the EPDC initialization script
            remarkable_dir = os.path.join(mount_point, 'var', 'lib', 'remarkable')
            os.makedirs(remarkable_dir, exist_ok=True)
            
            epdc_init_path = os.path.join(remarkable_dir, 'epdc-init-auto')
            
            with open(epdc_init_path, 'w') as f:
                f.write('#!/bin/sh\n')
                f.write('echo 1 > /sys/class/graphics/fb0/epdc_update_mode\n')
            
            # Make the script executable
            os.chmod(epdc_init_path, 0o755)
            
            logger.info("Xorg installed successfully")
            return True
        except Exception as e:
            logger.error("Error installing Xorg: %s", str(e))
            return False
    
    def _install_xfce(self, mount_point: str) -> bool:
        """
        Install Xfce
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if Xfce was installed successfully, False otherwise
        """
        try:
            logger.info("Installing Xfce...")
            
            # Create a pacman command to install Xfce
            pacman_cmd = [
                'chroot',
                mount_point,
                'pacman',
                '-S',
                '--noconfirm',
                'exo',
                'garcon',
                'thunar',
                'thunar-volman',
                'tumbler',
                'xfce4-appfinder',
                'xfce4-panel',
                'xfce4-session',
                'xfce4-settings',
                'xfce4-terminal',
                'xfconf',
                'xfdesktop',
                'xfwm4',
                'xfwm4-themes'
            ]
            
            # Run the pacman command
            returncode, stdout, stderr = self.env_manager.run_command(
                pacman_cmd,
                cwd=None
            )
            
            if returncode != 0:
                logger.error("Failed to install Xfce: %s", stderr)
                return False
            
            logger.info("Xfce installed successfully")
            return True
        except Exception as e:
            logger.error("Error installing Xfce: %s", str(e))
            return False
    
    def _configure_auto_loading(self, mount_point: str) -> bool:
        """
        Configure automatic loading of the desktop environment
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if automatic loading was configured successfully, False otherwise
        """
        try:
            logger.info("Configuring automatic loading of the desktop environment...")
            
            # Create the root user's home directory if it doesn't exist
            root_home = os.path.join(mount_point, 'root')
            os.makedirs(root_home, exist_ok=True)
            
            # Create .xserverrc
            xserverrc_path = os.path.join(root_home, '.xserverrc')
            
            with open(xserverrc_path, 'w') as f:
                f.write('#!/bin/sh\n')
                f.write('/var/lib/remarkable/epdc-init-auto\n')
                f.write('exec /usr/bin/Xorg -nocursor\n')
            
            # Make the script executable
            os.chmod(xserverrc_path, 0o755)
            
            # Create .xinitrc
            xinitrc_path = os.path.join(root_home, '.xinitrc')
            
            with open(xinitrc_path, 'w') as f:
                f.write('export GTK_OVERLAY_SCROLLING=0\n')
                f.write('dbus-launch xfce4-session\n')
            
            # Make the script executable
            os.chmod(xinitrc_path, 0o755)
            
            # Create .bash_profile
            bash_profile_path = os.path.join(root_home, '.bash_profile')
            
            with open(bash_profile_path, 'w') as f:
                f.write('if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then\n')
                f.write('    startx\n')
                f.write('fi\n')
            
            logger.info("Automatic loading configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring automatic loading: %s", str(e))
            return False
    
    def _configure_epaper_optimizations(self, mount_point: str) -> bool:
        """
        Configure e-paper optimizations
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if e-paper optimizations were configured successfully, False otherwise
        """
        try:
            logger.info("Configuring e-paper optimizations...")
            
            # Install Onboard virtual keyboard
            if self.desktop_config.get('input', {}).get('virtual_keyboard', {}).get('enable', True):
                pacman_cmd = [
                    'chroot',
                    mount_point,
                    'pacman',
                    '-S',
                    '--noconfirm',
                    'onboard',
                    'ttf-dejavu'
                ]
                
                returncode, stdout, stderr = self.env_manager.run_command(
                    pacman_cmd,
                    cwd=None
                )
                
                if returncode != 0:
                    logger.error("Failed to install Onboard virtual keyboard: %s", stderr)
                    return False
            
            # Create a script to configure Xfce settings
            xfce_config_path = os.path.join(mount_point, 'root', 'configure-xfce.sh')
            
            with open(xfce_config_path, 'w') as f:
                f.write('#!/bin/sh\n\n')
                
                # Disable overlay scrolling
                if self.desktop_config.get('ui', {}).get('epaper_optimizations', {}).get('disable_overlay_scrolling', True):
                    f.write('# Disable overlay scrolling\n')
                    f.write('gsettings set org.gnome.desktop.interface overlay-scrolling false\n\n')
                
                # Configure appearance
                f.write('# Configure appearance\n')
                f.write(f'xfconf-query -c xsettings -p /Net/ThemeName -s "{self.desktop_config.get("ui", {}).get("theme", "High Contrast")}"\n')
                f.write(f'xfconf-query -c xsettings -p /Net/IconThemeName -s "{self.desktop_config.get("ui", {}).get("icon_theme", "High Contrast")}"\n')
                
                # Configure fonts
                font = self.desktop_config.get('ui', {}).get('font', {})
                f.write('# Configure fonts\n')
                f.write(f'xfconf-query -c xsettings -p /Gtk/FontName -s "{font.get("default_font", "System-ui Regular")}"\n')
                
                if font.get('disable_antialiasing', True):
                    f.write('xfconf-query -c xsettings -p /Xft/Antialias -s 0\n')
                
                if not font.get('custom_dpi', False):
                    f.write('xfconf-query -c xsettings -p /Xft/DPI -s -1\n')
                
                # Configure toolbar style
                f.write('# Configure toolbar style\n')
                f.write('xfconf-query -c xsettings -p /Gtk/ToolbarStyle -s "text"\n')
                
                # Disable button and menu images
                if self.desktop_config.get('ui', {}).get('epaper_optimizations', {}).get('disable_button_images', True):
                    f.write('# Disable button images\n')
                    f.write('xfconf-query -c xsettings -p /Gtk/ButtonImages -s 0\n')
                
                if self.desktop_config.get('ui', {}).get('epaper_optimizations', {}).get('disable_menu_images', True):
                    f.write('# Disable menu images\n')
                    f.write('xfconf-query -c xsettings -p /Gtk/MenuImages -s 0\n')
                
                # Configure desktop background
                f.write('# Configure desktop background\n')
                f.write('xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/color-style -s 0\n')
                f.write('xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/rgba1 -s "ffffff"\n')
                f.write('xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/image-style -s 0\n')
                
                # Configure window manager
                f.write('# Configure window manager\n')
                f.write('xfconf-query -c xfwm4 -p /general/theme -s "Default-xhdpi"\n')
                f.write('xfconf-query -c xfwm4 -p /general/title_font -s "System-ui Bold"\n')
                
                # Disable shadows
                if self.desktop_config.get('ui', {}).get('epaper_optimizations', {}).get('disable_shadows', True):
                    f.write('# Disable shadows\n')
                    f.write('xfconf-query -c xfwm4 -p /general/show_dock_shadow -s false\n')
                    f.write('xfconf-query -c xfwm4 -p /general/show_frame_shadow -s false\n')
                
                # Configure panel
                f.write('# Configure panel\n')
                f.write('xfconf-query -c xfce4-panel -p /panels/panel-1/size -s 50\n')
                f.write('xfconf-query -c xfce4-panel -p /panels/panel-1/icon-size -s 32\n')
            
            # Make the script executable
            os.chmod(xfce_config_path, 0o755)
            
            # Add the script to .xinitrc
            xinitrc_path = os.path.join(mount_point, 'root', '.xinitrc')
            
            with open(xinitrc_path, 'r') as f:
                content = f.read()
            
            content = content.replace('dbus-launch xfce4-session', '# Configure Xfce settings\n~/configure-xfce.sh\n\ndbus-launch xfce4-session')
            
            with open(xinitrc_path, 'w') as f:
                f.write(content)
            
            logger.info("E-paper optimizations configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring e-paper optimizations: %s", str(e))
            return False
    
    def _configure_input_methods(self, mount_point: str) -> bool:
        """
        Configure input methods
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if input methods were configured successfully, False otherwise
        """
        try:
            logger.info("Configuring input methods...")
            
            # Configure virtual keyboard
            virtual_keyboard = self.desktop_config.get('input', {}).get('virtual_keyboard', {})
            
            if virtual_keyboard.get('enable', True):
                # Add Onboard to autostart
                autostart_dir = os.path.join(mount_point, 'etc', 'xdg', 'autostart')
                os.makedirs(autostart_dir, exist_ok=True)
                
                onboard_desktop_path = os.path.join(autostart_dir, 'onboard.desktop')
                
                with open(onboard_desktop_path, 'w') as f:
                    f.write('[Desktop Entry]\n')
                    f.write('Type=Application\n')
                    f.write('Name=Onboard\n')
                    f.write('Exec=onboard\n')
                    f.write('Icon=onboard\n')
                    f.write('X-GNOME-Autostart-enabled=true\n')
                    f.write('NoDisplay=false\n')
                    f.write('Hidden=false\n')
                    f.write('Comment=Virtual Keyboard\n')
                    f.write('X-GNOME-Autostart-Phase=Applications\n')
            
            logger.info("Input methods configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring input methods: %s", str(e))
            return False
    
    def configure_battery_monitor(self, mount_point: str) -> bool:
        """
        Configure battery charge indicator
        
        Args:
            mount_point: Mount point for the system partition
        
        Returns:
            True if battery charge indicator was configured successfully, False otherwise
        """
        try:
            logger.info("Configuring battery charge indicator...")
            
            # Install xfce4-genmon-plugin
            pacman_cmd = [
                'chroot',
                mount_point,
                'pacman',
                '-S',
                '--noconfirm',
                'xfce4-genmon-plugin'
            ]
            
            returncode, stdout, stderr = self.env_manager.run_command(
                pacman_cmd,
                cwd=None
            )
            
            if returncode != 0:
                logger.error("Failed to install xfce4-genmon-plugin: %s", stderr)
                return False
            
            # Create the battery monitor script
            battery_monitor_path = os.path.join(mount_point, 'usr', 'sbin', 'battery-monitor.sh')
            
            with open(battery_monitor_path, 'w') as f:
                f.write('#!/usr/bin/env bash\n\n')
                f.write('# battery-monitor.sh\n')
                f.write('# Prints the state of charge of the tablet\'s battery\n')
                f.write('#\n')
                f.write('# Parabola-rM is a free operating system for the reMarakble tablet.\n')
                f.write('# Copyright (C) 2020  Davis Remmel\n')
                f.write('#\n')
                f.write('# This program is free software: you can redistribute it and/or modify\n')
                f.write('# it under the terms of the GNU General Public License as published by\n')
                f.write('# the Free Software Foundation, either version 3 of the License, or\n')
                f.write('# (at your option) any later version.\n')
                f.write('#\n')
                f.write('# This program is distributed in the hope that it will be useful,\n')
                f.write('# but WITHOUT ANY WARRANTY; without even the implied warranty of\n')
                f.write('# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n')
                f.write('# GNU General Public License for more details.\n')
                f.write('#\n')
                f.write('# You should have received a copy of the GNU General Public License\n')
                f.write('# along with this program.  If not, see <https://www.gnu.org/licenses/>.\n\n')
                f.write('# Path for Linux 4.9\n')
                f.write('battpath="/sys/class/power_supply/bq27441-0"\n\n')
                f.write('chargenow="$(cat $battpath/charge_now)"\n')
                f.write('chargefull="$(cat $battpath/charge_full)"\n')
                f.write('status="$(cat $battpath/status)"\n\n')
                f.write('chargepct="$(echo $chargenow $chargefull \\\n')
                f.write('                   | awk \'{printf "%f", $1 / $2 * 100}\' \\\n')
                f.write('                   | cut -d\'.\' -f1)"\n\n')
                f.write('symbol=""\n')
                f.write('if [[ "Charging" == "$status" ]]\n')
                f.write('then\n')
                f.write('    symbol=$\'\\u26a1\'  # Lightning symbol\n')
                f.write('fi\n\n')
                f.write('echo "${symbol}${chargepct}%"\n')
            
            # Make the script executable
            os.chmod(battery_monitor_path, 0o755)
            
            # Add the battery monitor to the panel
            xfce_config_path = os.path.join(mount_point, 'root', 'configure-xfce.sh')
            
            with open(xfce_config_path, 'a') as f:
                f.write('\n# Add battery monitor to panel\n')
                f.write('xfce4-panel --add=genmon\n')
                f.write('# Configure the battery monitor\n')
                f.write('xfconf-query -c xfce4-panel -p /plugins/plugin-1/command -s "/usr/sbin/battery-monitor.sh"\n')
                f.write('xfconf-query -c xfce4-panel -p /plugins/plugin-1/use-label -s false\n')
            
            logger.info("Battery charge indicator configured successfully")
            return True
        except Exception as e:
            logger.error("Error configuring battery charge indicator: %s", str(e))
            return False