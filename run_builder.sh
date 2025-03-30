#!/bin/bash
# Run the Parabola RM Builder with the default configuration

# Exit on error
set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Go to the project root directory
cd "${SCRIPT_DIR}"

# Check if the virtual environment exists
if [ -d "venv" ]; then
    # Activate the virtual environment
    source venv/bin/activate
fi

# Run the builder
bin/parabola-rm-builder "$@"