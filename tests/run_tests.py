#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Runner for Parabola RM Builder

This script runs all the tests for the Parabola RM Builder.
"""

import os
import sys
import unittest
import argparse

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests(verbose=False, test_pattern=None):
    """
    Run the tests
    
    Args:
        verbose: Whether to run the tests in verbose mode
        test_pattern: Pattern to match test names
    
    Returns:
        True if all tests passed, False otherwise
    """
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Load the tests
    if test_pattern:
        suite = loader.loadTestsFromName(test_pattern)
    else:
        suite = loader.discover(os.path.dirname(os.path.abspath(__file__)))
    
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    
    # Run the tests
    result = runner.run(suite)
    
    # Return True if all tests passed, False otherwise
    return result.wasSuccessful()

def main():
    """
    Main entry point
    
    Returns:
        Exit code
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run tests for Parabola RM Builder')
    parser.add_argument('-v', '--verbose', action='store_true', help='Run tests in verbose mode')
    parser.add_argument('-p', '--pattern', help='Pattern to match test names')
    args = parser.parse_args()
    
    # Run the tests
    success = run_tests(args.verbose, args.pattern)
    
    # Return 0 if all tests passed, 1 otherwise
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())