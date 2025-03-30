#!/bin/bash
# Configure the desktop environment for Parabola RM

# Exit on error
set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Go to the project root directory
cd "${SCRIPT_DIR}"

# Parse command line arguments
DEVICE="/dev/mmcblk1"
while [[ $# -gt 0 ]]; do
    case $1 in
        --device)
            DEVICE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if the device exists
if [ ! -b "${DEVICE}" ]; then
    echo "Error: Device ${DEVICE} does not exist or is not a block device"
    exit 1
fi

# Create mount points
echo "Creating mount points..."
mkdir -p mnt/{p1,p2,p3}

# Mount the partitions
echo "Mounting the partitions..."
mount "${DEVICE}p1" mnt/p1
mount "${DEVICE}p2" mnt/p2
mount "${DEVICE}p3" mnt/p3

# Install Xorg
echo "Installing Xorg..."
chroot mnt/p2 pacman -S --noconfirm xorg-server xf86-video-fbdev xf86-input-evdev

# Create Xorg configuration
echo "Creating Xorg configuration..."
mkdir -p mnt/p2/etc/X11
cat > mnt/p2/etc/X11/xorg.conf << EOF
Section "ServerLayout"
    Identifier     "Default Layout"
    Screen         0 "Screen0" 0 0
    InputDevice    "Wacom" "CorePointer"
    InputDevice    "Touchscreen" "CorePointer"
    InputDevice    "Keyboard0" "CoreKeyboard"
EndSection

Section "InputDevice"
    Identifier     "Keyboard0"
    Driver         "kbd"
    Option         "XkbLayout" "us"
EndSection

Section "InputDevice"
    Identifier     "Wacom"
    Driver         "evdev"
    Option         "Device" "/dev/input/event1"
    Option         "Name" "Wacom I2C Digitizer"
    Option         "Calibration" "0 20966 0 15725"
    Option         "InvertY" "true"
EndSection

Section "InputDevice"
    Identifier     "Touchscreen"
    Driver         "evdev"
    Option         "Device" "/dev/input/event2"
    Option         "Name" "cyttsp5_mt"
    Option         "Calibration" "0 20966 0 15725"
    Option         "InvertY" "true"
EndSection

Section "Device"
    Identifier     "Card0"
    Driver         "fbdev"
    Option         "fbdev" "/dev/fb0"
EndSection

Section "Screen"
    Identifier     "Screen0"
    Device         "Card0"
    DefaultDepth    16
EndSection
EOF

# Create EPDC initialization script
echo "Creating EPDC initialization script..."
mkdir -p mnt/p2/var/lib/remarkable
cat > mnt/p2/var/lib/remarkable/epdc-init-auto << EOF
#!/bin/sh
echo 1 > /sys/class/graphics/fb0/epdc_update_mode
EOF
chmod +x mnt/p2/var/lib/remarkable/epdc-init-auto

# Install Xfce
echo "Installing Xfce..."
chroot mnt/p2 pacman -S --noconfirm exo garcon thunar thunar-volman tumbler xfce4-appfinder xfce4-panel xfce4-session xfce4-settings xfce4-terminal xfconf xfdesktop xfwm4 xfwm4-themes

# Configure automatic loading
echo "Configuring automatic loading..."
cat > mnt/p2/root/.xserverrc << EOF
#!/bin/sh
/var/lib/remarkable/epdc-init-auto
exec /usr/bin/Xorg -nocursor
EOF
chmod +x mnt/p2/root/.xserverrc

cat > mnt/p2/root/.xinitrc << EOF
export GTK_OVERLAY_SCROLLING=0
# Configure Xfce settings
~/configure-xfce.sh

dbus-launch xfce4-session
EOF
chmod +x mnt/p2/root/.xinitrc

cat > mnt/p2/root/.bash_profile << EOF
if [[ -z \$DISPLAY ]] && [[ \$(tty) = /dev/tty1 ]]; then
    startx
fi
EOF

# Configure automatic login
echo "Configuring automatic login..."
sed -i 's/ExecStart=-\/sbin\/agetty.*/ExecStart=-\/sbin\/agetty -a root --noclear %I $TERM/' mnt/p2/etc/systemd/system/getty.target.wants/getty@tty1.service

# Install Onboard virtual keyboard
echo "Installing Onboard virtual keyboard..."
chroot mnt/p2 pacman -S --noconfirm onboard ttf-dejavu

# Create Xfce configuration script
echo "Creating Xfce configuration script..."
cat > mnt/p2/root/configure-xfce.sh << EOF
#!/bin/sh

# Disable overlay scrolling
gsettings set org.gnome.desktop.interface overlay-scrolling false

# Configure appearance
xfconf-query -c xsettings -p /Net/ThemeName -s "High Contrast"
xfconf-query -c xsettings -p /Net/IconThemeName -s "High Contrast"

# Configure fonts
xfconf-query -c xsettings -p /Gtk/FontName -s "System-ui Regular"
xfconf-query -c xsettings -p /Xft/Antialias -s 0
xfconf-query -c xsettings -p /Xft/DPI -s -1

# Configure toolbar style
xfconf-query -c xsettings -p /Gtk/ToolbarStyle -s "text"

# Disable button and menu images
xfconf-query -c xsettings -p /Gtk/ButtonImages -s 0
xfconf-query -c xsettings -p /Gtk/MenuImages -s 0

# Configure desktop background
xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/color-style -s 0
xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/rgba1 -s "ffffff"
xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/image-style -s 0

# Configure window manager
xfconf-query -c xfwm4 -p /general/theme -s "Default-xhdpi"
xfconf-query -c xfwm4 -p /general/title_font -s "System-ui Bold"

# Disable shadows
xfconf-query -c xfwm4 -p /general/show_dock_shadow -s false
xfconf-query -c xfwm4 -p /general/show_frame_shadow -s false

# Configure panel
xfconf-query -c xfce4-panel -p /panels/panel-1/size -s 50
xfconf-query -c xfce4-panel -p /panels/panel-1/icon-size -s 32

# Add battery monitor to panel
xfce4-panel --add=genmon
# Configure the battery monitor
xfconf-query -c xfce4-panel -p /plugins/plugin-1/command -s "/usr/sbin/battery-monitor.sh"
xfconf-query -c xfce4-panel -p /plugins/plugin-1/use-label -s false
EOF
chmod +x mnt/p2/root/configure-xfce.sh

# Create battery monitor script
echo "Creating battery monitor script..."
mkdir -p mnt/p2/usr/sbin
cat > mnt/p2/usr/sbin/battery-monitor.sh << EOF
#!/usr/bin/env bash

# battery-monitor.sh
# Prints the state of charge of the tablet's battery
#
# Parabola-rM is a free operating system for the reMarakble tablet.
# Copyright (C) 2020  Davis Remmel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Path for Linux 4.9
battpath="/sys/class/power_supply/bq27441-0"

chargenow="\$(cat \$battpath/charge_now)"
chargefull="\$(cat \$battpath/charge_full)"
status="\$(cat \$battpath/status)"

chargepct="\$(echo \$chargenow \$chargefull \\
                   | awk '{printf "%f", \$1 / \$2 * 100}' \\
                   | cut -d'.' -f1)"

symbol=""
if [[ "Charging" == "\$status" ]]
then
    symbol=\$'\\u26a1'  # Lightning symbol
fi

echo "\${symbol}\${chargepct}%"
EOF
chmod +x mnt/p2/usr/sbin/battery-monitor.sh

# Configure graceful shutdown
echo "Configuring graceful shutdown..."
cat > mnt/p2/var/lib/remarkable/shutdown.sh << EOF
#!/usr/bin/env bash
pgrep Xorg | xargs wait
sleep 1
journalctl --vacuum-size=100M
/var/lib/remarkable/epdc-show-bitmap /var/lib/uboot/splash-off.raw
EOF
chmod +x mnt/p2/var/lib/remarkable/shutdown.sh

cat > mnt/p2/etc/systemd/system/remarkable-shutdown.service << EOF
[Unit]
Description=rM shutdown helper

[Service]
Type=oneshot
RemainAfterExit=true
ExecStop=/var/lib/remarkable/shutdown.sh

[Install]
WantedBy=multi-user.target
EOF

# Enable services
echo "Enabling services..."
chroot mnt/p2 systemctl enable systemd-networkd
chroot mnt/p2 systemctl enable dnsmasq
chroot mnt/p2 systemctl enable remarkable-shutdown.service

# Unmount the partitions
echo "Unmounting the partitions..."
umount mnt/p1
umount mnt/p2
umount mnt/p3

# Remove the mount points
echo "Removing mount points..."
rmdir mnt/{p1,p2,p3}
rmdir mnt

echo "Desktop environment configured successfully!"