#!/bin/bash
# Install the reMarkable toolchain for direct use

# Exit on error
set -e

# Print commands
set -x

# Default installation path
INSTALL_PATH="${HOME}/.parabola-rm-builder/toolchain"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --install-path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create the installation directory
mkdir -p "${INSTALL_PATH}"

# Download the toolchain
echo "Downloading reMarkable toolchain..."
wget -q https://ipfs.eeems.website/ipfs/Qmdkdeh3bodwDLM9YvPrMoAi6dFYDDCodAnHvjG5voZxiC -O "${INSTALL_PATH}/toolchain.tar.gz"

# Extract the toolchain
echo "Extracting toolchain..."
tar xf "${INSTALL_PATH}/toolchain.tar.gz" -C "${INSTALL_PATH}"

# Remove the archive
rm "${INSTALL_PATH}/toolchain.tar.gz"

# Create a script to set up the environment
cat > "${INSTALL_PATH}/setup_env.sh" << 'EOF'
#!/bin/bash
# Set up the environment for the reMarkable toolchain

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the environment setup script
source "${SCRIPT_DIR}/poky-2.1.3/environment-setup-armv7at2hf-neon-poky-linux-gnueabi"

# Print a message
echo "Environment set up for reMarkable toolchain"
echo "You can now compile software for the reMarkable tablet"
EOF

# Make the script executable
chmod +x "${INSTALL_PATH}/setup_env.sh"

echo "Toolchain installed successfully to ${INSTALL_PATH}"
echo "To set up the environment, run: source ${INSTALL_PATH}/setup_env.sh"