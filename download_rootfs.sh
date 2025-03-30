#!/bin/bash
# Download and extract the Parabola rootfs

# Exit on error
set -e

# Print commands
set -x

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Go to the project root directory
cd "${SCRIPT_DIR}"

# Create build and output directories if they don't exist
mkdir -p build/rootfs output/rootfs

# Download the Parabola rootfs
echo "Downloading Parabola rootfs..."
wget -q https://repo.parabola.nu/iso/armv7h/parabola-systemd-cli-armv7h-latest.tar.gz -O build/rootfs/parabola-rootfs.tar.gz

# Extract the rootfs to the output directory
echo "Extracting Parabola rootfs..."
mkdir -p output/rootfs/system
tar xf build/rootfs/parabola-rootfs.tar.gz -C output/rootfs/system

echo "Parabola rootfs downloaded and extracted successfully!"
echo "Rootfs is in: ${SCRIPT_DIR}/output/rootfs/system/"