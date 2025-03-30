#!/bin/bash
# Initialize the development environment for Parabola RM Builder

# Exit on error
set -e

# Print commands
set -x

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install the package in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Make the main executable script executable
chmod +x bin/parabola-rm-builder

# Create output directory
mkdir -p output

# Create build directory
mkdir -p build

echo "Development environment initialized successfully!"
echo "To activate the virtual environment, run: source venv/bin/activate"