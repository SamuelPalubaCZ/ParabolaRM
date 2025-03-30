#!/bin/bash
# Build and install Parabola RM

# Exit on error
set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Go to the project root directory
cd "${SCRIPT_DIR}"

# Parse command line arguments
DEVICE="/dev/mmcblk1"
SKIP_BUILD=false
SKIP_ROOTFS=false
SKIP_INSTALL=false
SKIP_DESKTOP=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --device)
            DEVICE="$2"
            shift 2
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-rootfs)
            SKIP_ROOTFS=true
            shift
            ;;
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        --skip-desktop)
            SKIP_DESKTOP=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --device DEVICE    Device to install to (default: /dev/mmcblk1)"
            echo "  --skip-build       Skip building the kernel and bootloader"
            echo "  --skip-rootfs      Skip downloading the rootfs"
            echo "  --skip-install     Skip installing to the device"
            echo "  --skip-desktop     Skip configuring the desktop environment"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if the device exists
if [ ! -b "${DEVICE}" ] && [ "${SKIP_INSTALL}" = false ]; then
    echo "Error: Device ${DEVICE} does not exist or is not a block device"
    exit 1
fi

# Build the kernel and bootloader
if [ "${SKIP_BUILD}" = false ]; then
    echo "Building kernel and bootloader..."
    ./download_and_build.sh
fi

# Download the rootfs
if [ "${SKIP_ROOTFS}" = false ]; then
    echo "Downloading rootfs..."
    ./download_rootfs.sh
fi

# Install to the device
if [ "${SKIP_INSTALL}" = false ]; then
    echo "Installing to device..."
    ./install_to_device.sh --device "${DEVICE}"
fi

# Configure the desktop environment
if [ "${SKIP_DESKTOP}" = false ] && [ "${SKIP_INSTALL}" = false ]; then
    echo "Configuring desktop environment..."
    ./configure_desktop.sh --device "${DEVICE}"
fi

echo "Build and installation completed successfully!"
if [ "${SKIP_INSTALL}" = false ]; then
    echo "You can now boot your reMarkable tablet with Parabola RM."
fi