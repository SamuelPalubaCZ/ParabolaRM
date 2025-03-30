#!/bin/bash
# Download, extract, and build components based on links.txt

# Exit on error
set -e

# Print commands
set -x

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Go to the project root directory
cd "${SCRIPT_DIR}"

# Create build and output directories if they don't exist
mkdir -p build/kernel build/toolchain output/kernel output/bootloader

# Parse links.txt
KERNEL_REPO=$(grep "kernel default" ../links.txt | cut -d'=' -f1 | tr -d ' ')
TOOLCHAIN_URL=$(grep "toolchain" ../links.txt | cut -d'=' -f1 | tr -d ' ')

echo "Kernel repository: ${KERNEL_REPO}"
echo "Toolchain URL: ${TOOLCHAIN_URL}"

# Download and extract toolchain
echo "Downloading toolchain..."
wget -q "${TOOLCHAIN_URL}" -O build/toolchain/toolchain.tar.gz

echo "Extracting toolchain..."
tar xf build/toolchain/toolchain.tar.gz -C build/toolchain
rm build/toolchain/toolchain.tar.gz

# Set up environment variables for cross-compilation
source build/toolchain/poky-2.1.3/environment-setup-armv7at2hf-neon-poky-linux-gnueabi

# Clone kernel repository if it doesn't exist
if [ ! -d "build/kernel/linux" ]; then
    echo "Cloning kernel repository..."
    git clone --branch lars/zero-gravitas_4.9 https://${KERNEL_REPO} build/kernel/linux
else
    echo "Updating kernel repository..."
    cd build/kernel/linux
    git pull
    cd "${SCRIPT_DIR}"
fi

# Apply kernel patches
echo "Applying kernel patches..."
cd build/kernel/linux
for patch_file in "${SCRIPT_DIR}/resources/patches/kernel"/*.patch; do
    if [ -f "${patch_file}" ]; then
        echo "Applying patch: ${patch_file}"
        git apply "${patch_file}"
    fi
done

# Remove proprietary blobs
echo "Removing proprietary blobs..."
find firmware -type f | grep -v 'epdc_ES103CS1.fw.ihex' | xargs rm -f || true

# Configure kernel
echo "Configuring kernel..."
make zero-gravitas_defconfig

# Modify kernel configuration
echo "Modifying kernel configuration..."
# Enable automatic partial refreshing
sed -i 's/# CONFIG_FB_MXC_EINK_AUTO_UPDATE_MODE is not set/CONFIG_FB_MXC_EINK_AUTO_UPDATE_MODE=y/' .config
# Enable USB ACM
sed -i 's/# CONFIG_USB_ACM is not set/CONFIG_USB_ACM=y/' .config
# Enable USB F_ACM
sed -i 's/# CONFIG_USB_F_ACM is not set/CONFIG_USB_F_ACM=y/' .config
# Enable USB U_SERIAL
sed -i 's/# CONFIG_USB_U_SERIAL is not set/CONFIG_USB_U_SERIAL=y/' .config
# Enable USB CDC COMPOSITE
sed -i 's/# CONFIG_USB_CDC_COMPOSITE is not set/CONFIG_USB_CDC_COMPOSITE=y/' .config
# Disable BRCMFMAC
sed -i 's/CONFIG_BRCMFMAC=m/# CONFIG_BRCMFMAC is not set/' .config
# Disable TOUCHSCREEN_CYPRESS_CYTTSP5_LOADER
sed -i 's/CONFIG_TOUCHSCREEN_CYPRESS_CYTTSP5_LOADER=y/# CONFIG_TOUCHSCREEN_CYPRESS_CYTTSP5_LOADER is not set/' .config
# Disable TOUCHSCREEN_CYPRESS_CYTTSP5_BINARY_FW_UPGRADE
sed -i 's/CONFIG_TOUCHSCREEN_CYPRESS_CYTTSP5_BINARY_FW_UPGRADE=y/# CONFIG_TOUCHSCREEN_CYPRESS_CYTTSP5_BINARY_FW_UPGRADE is not set/' .config
# Disable IMX_SDMA
sed -i 's/CONFIG_IMX_SDMA=y/# CONFIG_IMX_SDMA is not set/' .config

# Build kernel
echo "Building kernel..."
make -j$(nproc)

# Copy kernel files to output directory
echo "Copying kernel files to output directory..."
cp arch/arm/boot/zImage "${SCRIPT_DIR}/output/kernel/"
cp arch/arm/boot/dts/zero-gravitas.dtb "${SCRIPT_DIR}/output/kernel/"
cp firmware/epdc_ES103CS1.fw.ihex "${SCRIPT_DIR}/output/kernel/"

cd "${SCRIPT_DIR}"

# Clone U-Boot repository if it doesn't exist
if [ ! -d "build/bootloader/uboot" ]; then
    echo "Cloning U-Boot repository..."
    git clone https://github.com/remarkable/uboot.git build/bootloader/uboot
else
    echo "Updating U-Boot repository..."
    cd build/bootloader/uboot
    git pull
    cd "${SCRIPT_DIR}"
fi

# Apply U-Boot patches
echo "Applying U-Boot patches..."
cd build/bootloader/uboot
for patch_file in "${SCRIPT_DIR}/resources/patches/bootloader"/*.patch; do
    if [ -f "${patch_file}" ]; then
        echo "Applying patch: ${patch_file}"
        git apply "${patch_file}"
    fi
done

# Build U-Boot
echo "Building U-Boot..."
make zero-gravitas_defconfig
make -j$(nproc)

# Copy U-Boot files to output directory
echo "Copying U-Boot files to output directory..."
cp u-boot.imx "${SCRIPT_DIR}/output/bootloader/"

cd "${SCRIPT_DIR}"

echo "Download and build completed successfully!"
echo "Kernel files are in: ${SCRIPT_DIR}/output/kernel/"
echo "Bootloader files are in: ${SCRIPT_DIR}/output/bootloader/"