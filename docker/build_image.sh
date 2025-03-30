#!/bin/bash
# Build the Docker image for the cross-compilation environment

# Exit on error
set -e

# Print commands
set -x

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Go to the project root directory
cd "${SCRIPT_DIR}/.."

# Build the Docker image
docker build -t parabola-rm-builder-toolchain:latest -f docker/toolchain/Dockerfile docker/toolchain

echo "Docker image built successfully!"
echo "You can now use the containerized cross-compilation environment."