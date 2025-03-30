#!/bin/bash
# Create a release package for Parabola RM Builder

# Exit on error
set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Go to the project root directory
cd "${SCRIPT_DIR}"

# Parse command line arguments
VERSION="0.1.0"
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "${TEMP_DIR}"' EXIT

# Create the release directory
RELEASE_DIR="${TEMP_DIR}/parabola-rm-builder-${VERSION}"
mkdir -p "${RELEASE_DIR}"

# Copy the files to the release directory
cp -r bin config docker docs resources src tests .gitignore LICENSE README.md setup.py "${RELEASE_DIR}"

# Create the release archive
RELEASE_ARCHIVE="parabola-rm-builder-${VERSION}.tar.gz"
tar -czf "${RELEASE_ARCHIVE}" -C "${TEMP_DIR}" "parabola-rm-builder-${VERSION}"

echo "Release archive created: ${RELEASE_ARCHIVE}"