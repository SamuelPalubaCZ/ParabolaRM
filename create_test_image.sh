#!/bin/bash
# Create a test image for testing the installation

# Exit on error
set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Go to the project root directory
cd "${SCRIPT_DIR}"

# Parse command line arguments
IMAGE_SIZE="8G"
OUTPUT_FILE="test_image.img"
while [[ $# -gt 0 ]]; do
    case $1 in
        --size)
            IMAGE_SIZE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create the test image
echo "Creating test image of size ${IMAGE_SIZE}..."
dd if=/dev/zero of="${OUTPUT_FILE}" bs=1 count=0 seek="${IMAGE_SIZE}"

# Create a loop device for the image
echo "Creating loop device..."
LOOP_DEVICE=$(sudo losetup -f --show "${OUTPUT_FILE}")

# Clean up the loop device on exit
trap 'sudo losetup -d "${LOOP_DEVICE}" || true' EXIT

echo "Test image created: ${OUTPUT_FILE}"
echo "Loop device: ${LOOP_DEVICE}"
echo ""
echo "You can now use this image for testing the installation:"
echo "  ./run_builder.sh install --device ${LOOP_DEVICE}"
echo ""
echo "When you're done, you can detach the loop device:"
echo "  sudo losetup -d ${LOOP_DEVICE}"