#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command Line Interface for Parabola RM Builder

This module provides the command line interface for the Parabola RM Builder.
"""

import os
import sys
import argparse
import logging
import yaml
from typing import Dict, Any, List, Optional

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_manager.config_manager import ConfigManager
from src.cross_env.env_manager import CrossEnvManager
from src.builders.bootloader.uboot_builder import UBootBuilder
from src.builders.kernel.kernel_builder import KernelBuilder
from src.executor.installation_executor import InstallationExecutor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argparse() -> argparse.ArgumentParser:
    """
    Set up the argument parser
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Parabola RM Builder - A configurable builder for Parabola RM'
    )
    
    # Global options
    parser.add_argument(
        '-c', '--config',
        help='Path to the configuration file',
        default=None
    )
    parser.add_argument(
        '-v', '--verbose',
        help='Enable verbose output',
        action='store_true'
    )
    parser.add_argument(
        '--version',
        help='Show version information',
        action='store_true'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Command to execute'
    )
    
    # Init command
    init_parser = subparsers.add_parser(
        'init',
        help='Initialize a new configuration'
    )
    init_parser.add_argument(
        '-o', '--output',
        help='Path to save the configuration',
        default='parabola-rm-config.yaml'
    )
    
    # Build command
    build_parser = subparsers.add_parser(
        'build',
        help='Build components'
    )
    build_parser.add_argument(
        '--bootloader',
        help='Build the bootloader',
        action='store_true'
    )
    build_parser.add_argument(
        '--kernel',
        help='Build the kernel',
        action='store_true'
    )
    build_parser.add_argument(
        '--all',
        help='Build all components',
        action='store_true'
    )
    
    # Install command
    install_parser = subparsers.add_parser(
        'install',
        help='Install Parabola RM'
    )
    install_parser.add_argument(
        '--device',
        help='Device to install to',
        default='/dev/mmcblk1'
    )
    install_parser.add_argument(
        '--skip-build',
        help='Skip building components',
        action='store_true'
    )
    
    # Environment command
    env_parser = subparsers.add_parser(
        'env',
        help='Manage the cross-compilation environment'
    )
    env_parser.add_argument(
        '--setup',
        help='Set up the cross-compilation environment',
        action='store_true'
    )
    env_parser.add_argument(
        '--clean',
        help='Clean the cross-compilation environment',
        action='store_true'
    )
    
    return parser

def show_version() -> None:
    """
    Show version information
    """
    print("Parabola RM Builder v0.1.0")
    print("A configurable builder for Parabola RM")
    print("Copyright (c) 2025")

def init_config(args: argparse.Namespace, config_manager: ConfigManager) -> int:
    """
    Initialize a new configuration
    
    Args:
        args: Command line arguments
        config_manager: Configuration manager
    
    Returns:
        Exit code
    """
    try:
        # Load the default configuration
        config = config_manager.load_config()
        
        # Save the configuration to the output file
        config_manager.save_config(args.output)
        
        logger.info("Configuration initialized and saved to %s", args.output)
        return 0
    except Exception as e:
        logger.error("Failed to initialize configuration: %s", str(e))
        return 1

def setup_environment(args: argparse.Namespace, config_manager: ConfigManager) -> int:
    """
    Set up the cross-compilation environment
    
    Args:
        args: Command line arguments
        config_manager: Configuration manager
    
    Returns:
        Exit code
    """
    try:
        # Load the configuration
        config = config_manager.load_config()
        
        # Create the cross-compilation environment manager
        env_manager = CrossEnvManager(config)
        
        # Set up the environment
        if env_manager.setup_environment():
            logger.info("Cross-compilation environment set up successfully")
            return 0
        else:
            logger.error("Failed to set up cross-compilation environment")
            return 1
    except Exception as e:
        logger.error("Failed to set up environment: %s", str(e))
        return 1

def clean_environment(args: argparse.Namespace, config_manager: ConfigManager) -> int:
    """
    Clean the cross-compilation environment
    
    Args:
        args: Command line arguments
        config_manager: Configuration manager
    
    Returns:
        Exit code
    """
    # TODO: Implement environment cleaning
    logger.info("Environment cleaning not implemented yet")
    return 0

def build_components(args: argparse.Namespace, config_manager: ConfigManager) -> int:
    """
    Build components
    
    Args:
        args: Command line arguments
        config_manager: Configuration manager
    
    Returns:
        Exit code
    """
    try:
        # Load the configuration
        config = config_manager.load_config()
        
        # Create the cross-compilation environment manager
        env_manager = CrossEnvManager(config)
        
        # Set up the environment
        if not env_manager.setup_environment():
            logger.error("Failed to set up cross-compilation environment")
            return 1
        
        # Build components
        if args.all:
            # Use the installation executor to build all components
            executor = InstallationExecutor(config_manager, env_manager)
            if not executor._build_components():
                logger.error("Failed to build components")
                return 1
        else:
            # Build individual components
            if args.bootloader:
                logger.info("Building bootloader...")
                bootloader_builder = UBootBuilder(config, env_manager)
                if not bootloader_builder.build():
                    logger.error("Failed to build bootloader")
                    return 1
                logger.info("Bootloader built successfully")
            
            if args.kernel:
                logger.info("Building kernel...")
                kernel_builder = KernelBuilder(config, env_manager)
                if not kernel_builder.build():
                    logger.error("Failed to build kernel")
                    return 1
                logger.info("Kernel built successfully")
        
        logger.info("Build completed successfully")
        return 0
    except Exception as e:
        logger.error("Failed to build components: %s", str(e))
        return 1

def install_parabola(args: argparse.Namespace, config_manager: ConfigManager) -> int:
    """
    Install Parabola RM
    
    Args:
        args: Command line arguments
        config_manager: Configuration manager
    
    Returns:
        Exit code
    """
    try:
        # Load the configuration
        config = config_manager.load_config()
        
        # Create the cross-compilation environment manager
        env_manager = CrossEnvManager(config)
        
        # Set up the environment
        if not env_manager.setup_environment():
            logger.error("Failed to set up cross-compilation environment")
            return 1
        
        # Create the installation executor
        executor = InstallationExecutor(config_manager, env_manager)
        
        # Execute the installation
        if not executor.execute(args.device, args.skip_build):
            logger.error("Failed to install Parabola RM")
            return 1
        
        logger.info("Parabola RM installed successfully to %s", args.device)
        return 0
    except Exception as e:
        logger.error("Failed to install Parabola RM: %s", str(e))
        return 1

def main() -> int:
    """
    Main entry point
    
    Returns:
        Exit code
    """
    # Parse command line arguments
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Show version information
    if args.version:
        show_version()
        return 0
    
    # Create the configuration manager
    config_manager = ConfigManager(args.config)
    
    # Execute the command
    if args.command == 'init':
        return init_config(args, config_manager)
    elif args.command == 'env':
        if args.setup:
            return setup_environment(args, config_manager)
        elif args.clean:
            return clean_environment(args, config_manager)
        else:
            parser.print_help()
            return 1
    elif args.command == 'build':
        return build_components(args, config_manager)
    elif args.command == 'install':
        return install_parabola(args, config_manager)
    else:
        parser.print_help()
        return 0

if __name__ == '__main__':
    sys.exit(main())