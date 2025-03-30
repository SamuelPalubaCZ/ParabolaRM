#!/bin/bash
# Install Parabola RM to a device

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

# Check if the necessary files exist
if [ ! -f "output/bootloader/u-boot.imx" ]; then
    echo "Error: Bootloader not found. Please run download_and_build.sh first."
    exit 1
fi

if [ ! -f "output/kernel/zImage" ] || [ ! -f "output/kernel/zero-gravitas.dtb" ]; then
    echo "Error: Kernel files not found. Please run download_and_build.sh first."
    exit 1
fi

if [ ! -d "output/rootfs/system" ]; then
    echo "Error: Rootfs not found. Please run download_rootfs.sh first."
    exit 1
fi

echo "Installing Parabola RM to ${DEVICE}..."

# Partition the device
echo "Partitioning the device..."
cat << EOF | fdisk "${DEVICE}"
o
n
p
1
4096
+20M
t
c
a
n
p
2

+2G
n
p
3


w
EOF

# Wait for the kernel to recognize the new partition table
sleep 2

# Format the partitions
echo "Formatting the partitions..."
mkfs.vfat "${DEVICE}p1"
mkfs.ext4 -O '^64bit' -O '^metadata_csum' -O 'uninit_bg' -J 'size=4' -b 1024 -g 8192 -i 4096 -I 128 "${DEVICE}p2"
mkfs.ext4 -O '^64bit' -O '^metadata_csum' -O 'uninit_bg' -J 'size=4' -b 1024 -g 8192 -i 4096 -I 128 "${DEVICE}p3"

# Install the bootloader
echo "Installing the bootloader..."
echo 0 > "/sys/block/$(basename ${DEVICE})boot0/force_ro"
dd if=/dev/zero of="${DEVICE}boot0" bs=512 count=4096
dd if="output/bootloader/u-boot.imx" of="${DEVICE}boot0" bs=512 seek=2
echo 1 > "/sys/block/$(basename ${DEVICE})boot0/force_ro"

# Create mount points
echo "Creating mount points..."
mkdir -p mnt/{p1,p2,p3}

# Mount the partitions
echo "Mounting the partitions..."
mount "${DEVICE}p1" mnt/p1
mount "${DEVICE}p2" mnt/p2
mount "${DEVICE}p3" mnt/p3

# Install the kernel
echo "Installing the kernel..."
mkdir -p mnt/p2/boot
cp output/kernel/zImage mnt/p2/boot/
cp output/kernel/zero-gravitas.dtb mnt/p2/boot/

# Install the bootloader files
echo "Installing the bootloader files..."
cp output/kernel/epdc_ES103CS1.fw.ihex mnt/p1/waveform.bin
if [ -f "resources/assets/splash.bmp" ]; then
    cp resources/assets/splash.bmp mnt/p1/splash.bmp
fi

# Install the rootfs
echo "Installing the rootfs..."
cp -a output/rootfs/system/* mnt/p2/

# Create home directory
echo "Creating home directory..."
mkdir -p mnt/p3/root

# Configure fstab
echo "Configuring fstab..."
cat > mnt/p2/etc/fstab << EOF
/dev/mmcblk1p2  /               auto    defaults                    1  1
/dev/mmcblk1p1  /var/lib/uboot  auto    defaults                    0  0
/dev/mmcblk1p3  /home           auto    defaults                    0  2
devpts  /dev/pts        devpts  mode=0620,gid=5                     0  0
proc    /proc           proc    defaults                            0  0
tmpfs   /run            tmpfs   mode=0755,nodev,nosuid,strictatime  0  0
tmpfs   /tmp            tmpfs   defaults                            0  0
tmpfs   /root/.cache    tmpfs   defaults,size=20M                   0  0
EOF

# Configure serial console
echo "Configuring serial console..."
mkdir -p mnt/p2/etc/systemd/system/getty.target.wants
ln -sf /usr/lib/systemd/system/serial-getty@.service mnt/p2/etc/systemd/system/getty.target.wants/serial-getty@ttyGS0.service

# Configure PAM
echo "Configuring PAM..."
sed -i 's/auth       required     pam_securetty.so/#auth       required     pam_securetty.so/' mnt/p2/etc/pam.d/login
sed -i 's/session   optional   pam_systemd.so/#-session   optional   pam_systemd.so/' mnt/p2/etc/pam.d/system-login

# Configure network
echo "Configuring network..."
mkdir -p mnt/p2/etc/systemd/network
cat > mnt/p2/etc/systemd/network/usb0.network << EOF
[Match]
Name=usb0

[Network]
Address=10.11.99.1/24
EOF

# Configure DHCP server
echo "Configuring DHCP server..."
cat > mnt/p2/etc/dnsmasq.conf << EOF
interface=usb0
bind-interfaces
dhcp-range=10.11.99.2,10.11.99.253,10m
dhcp-option=6  # Don't send DNS
EOF

# Unmount the partitions
echo "Unmounting the partitions..."
umount mnt/p1
umount mnt/p2
umount mnt/p3

# Remove the mount points
echo "Removing mount points..."
rmdir mnt/{p1,p2,p3}
rmdir mnt

echo "Installation completed successfully!"
echo "You can now boot your reMarkable tablet with Parabola RM."