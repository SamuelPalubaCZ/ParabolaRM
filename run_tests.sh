#!/bin/bash
# Run the tests for Parabola RM Builder

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

# Run the tests
python -m tests.run_tests "$@"