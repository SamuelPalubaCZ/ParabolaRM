#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cross-Compilation Environment Manager for Parabola RM Builder

This module handles the setup and management of cross-compilation environments,
including both containerized and direct toolchain approaches.
"""

import os
import sys
import logging
import platform
import subprocess
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

class CrossEnvManager:
    """
    Cross-Compilation Environment Manager
    
    This class is responsible for setting up and managing the cross-compilation
    environment for the Parabola RM Builder.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Cross-Compilation Environment Manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.env_type = config.get('cross_compilation', {}).get('environment_type', 'container')
        self.toolchain_version = config.get('cross_compilation', {}).get('toolchain_version', 'latest')
        
        # Set up environment-specific configurations
        if self.env_type == 'container':
            self.container_config = config.get('cross_compilation', {}).get('container', {})
        else:
            self.direct_config = config.get('cross_compilation', {}).get('direct', {})
        
        # Build configuration
        self.build_config = config.get('cross_compilation', {}).get('build', {})
        
        # Environment variables for cross-compilation
        self.env_vars = {}
    
    def setup_environment(self) -> bool:
        """
        Set up the cross-compilation environment
        
        Returns:
            True if the environment was set up successfully, False otherwise
        """
        if self.env_type == 'container':
            return self._setup_container_environment()
        else:
            return self._setup_direct_environment()
    
    def _setup_container_environment(self) -> bool:
        """
        Set up the containerized cross-compilation environment
        
        Returns:
            True if the environment was set up successfully, False otherwise
        """
        logger.info("Setting up containerized cross-compilation environment")
        
        # Check if Docker/Podman is installed
        if not self._check_container_runtime():
            logger.error("Container runtime (Docker/Podman) not found")
            return False
        
        # Check if the container image exists
        image_name = self._get_container_image_name()
        if not self._check_container_image(image_name):
            # Build the container image
            if not self._build_container_image(image_name):
                logger.error("Failed to build container image")
                return False
        
        logger.info("Containerized environment set up successfully")
        return True
    
    def _setup_direct_environment(self) -> bool:
        """
        Set up the direct toolchain cross-compilation environment
        
        Returns:
            True if the environment was set up successfully, False otherwise
        """
        logger.info("Setting up direct toolchain cross-compilation environment")
        
        # Check if the toolchain is installed
        toolchain_path = self._get_toolchain_path()
        if not self._check_toolchain(toolchain_path):
            # Install the toolchain
            if not self._install_toolchain(toolchain_path):
                logger.error("Failed to install toolchain")
                return False
        
        # Set up environment variables
        self._setup_env_vars(toolchain_path)
        
        logger.info("Direct toolchain environment set up successfully")
        return True
    
    def _check_container_runtime(self) -> bool:
        """
        Check if Docker/Podman is installed
        
        Returns:
            True if Docker/Podman is installed, False otherwise
        """
        try:
            # Try Docker first
            result = subprocess.run(
                ['docker', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                logger.debug("Docker found: %s", result.stdout.decode().strip())
                self.container_runtime = 'docker'
                return True
            
            # Try Podman if Docker is not available
            result = subprocess.run(
                ['podman', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode == 0:
                logger.debug("Podman found: %s", result.stdout.decode().strip())
                self.container_runtime = 'podman'
                return True
            
            return False
        except Exception as e:
            logger.error("Error checking container runtime: %s", str(e))
            return False
    
    def _check_container_image(self, image_name: str) -> bool:
        """
        Check if the container image exists
        
        Args:
            image_name: Name of the container image
        
        Returns:
            True if the image exists, False otherwise
        """
        try:
            result = subprocess.run(
                [self.container_runtime, 'image', 'inspect', image_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            return result.returncode == 0
        except Exception as e:
            logger.error("Error checking container image: %s", str(e))
            return False
    
    def _build_container_image(self, image_name: str) -> bool:
        """
        Build the container image
        
        Args:
            image_name: Name of the container image
        
        Returns:
            True if the image was built successfully, False otherwise
        """
        try:
            # Generate Dockerfile
            dockerfile_path = self._generate_dockerfile()
            
            # Build the image
            logger.info("Building container image %s", image_name)
            
            build_cmd = [
                self.container_runtime, 'build',
                '-t', image_name,
                '-f', dockerfile_path,
                os.path.dirname(dockerfile_path)
            ]
            
            result = subprocess.run(
                build_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            if result.returncode != 0:
                logger.error("Failed to build container image: %s", result.stderr.decode())
                return False
            
            logger.info("Container image built successfully")
            return True
        except Exception as e:
            logger.error("Error building container image: %s", str(e))
            return False
    
    def _generate_dockerfile(self) -> str:
        """
        Generate a Dockerfile for the cross-compilation environment
        
        Returns:
            Path to the generated Dockerfile
        """
        # Create the dockerfiles directory if it doesn't exist
        dockerfiles_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'docker',
            'toolchain'
        )
        os.makedirs(dockerfiles_dir, exist_ok=True)
        
        # Generate the Dockerfile
        dockerfile_path = os.path.join(dockerfiles_dir, 'Dockerfile')
        
        with open(dockerfile_path, 'w') as f:
            f.write(f"FROM {self.container_config.get('base_image', 'debian:bullseye')}\n\n")
            
            # Set up environment variables
            f.write("ENV DEBIAN_FRONTEND=noninteractive\n")
            f.write("ENV TZ=UTC\n\n")
            
            # Install dependencies
            f.write("RUN apt-get update && \\\n")
            f.write("    apt-get install -y --no-install-recommends \\\n")
            f.write("        build-essential \\\n")
            f.write("        ca-certificates \\\n")
            f.write("        curl \\\n")
            f.write("        git \\\n")
            f.write("        make \\\n")
            f.write("        cmake \\\n")
            f.write("        python3 \\\n")
            f.write("        python3-pip \\\n")
            f.write("        wget \\\n")
            f.write("        xz-utils \\\n")
            f.write("        && \\\n")
            f.write("    apt-get clean && \\\n")
            f.write("    rm -rf /var/lib/apt/lists/*\n\n")
            
            # Install the toolchain
            f.write("# Download and install the reMarkable toolchain\n")
            f.write("RUN mkdir -p /opt/toolchain && \\\n")
            f.write("    cd /opt/toolchain && \\\n")
            f.write("    wget -q https://ipfs.eeems.website/ipfs/Qmdkdeh3bodwDLM9YvPrMoAi6dFYDDCodAnHvjG5voZxiC -O toolchain.tar.gz && \\\n")
            f.write("    tar xf toolchain.tar.gz && \\\n")
            f.write("    rm toolchain.tar.gz\n\n")
            
            # Set up environment variables for the toolchain
            f.write("# Set up environment variables\n")
            f.write("ENV PATH=\"/opt/toolchain/poky-2.1.3/sysroots/x86_64-pokysdk-linux/usr/bin:/opt/toolchain/poky-2.1.3/sysroots/x86_64-pokysdk-linux/usr/sbin:${PATH}\"\n")
            f.write("ENV OECORE_NATIVE_SYSROOT=\"/opt/toolchain/poky-2.1.3/sysroots/x86_64-pokysdk-linux\"\n")
            
            # Create a working directory
            f.write("\n# Create a working directory\n")
            f.write("WORKDIR /workspaces\n\n")
            
            # Set the entrypoint
            f.write("# Set the entrypoint\n")
            f.write("ENTRYPOINT [\"/bin/bash\"]\n")
        
        logger.debug("Generated Dockerfile at %s", dockerfile_path)
        return dockerfile_path
    
    def _get_container_image_name(self) -> str:
        """
        Get the name of the container image
        
        Returns:
            Name of the container image
        """
        return f"parabola-rm-builder-toolchain:{self.toolchain_version}"
    
    def _check_toolchain(self, toolchain_path: str) -> bool:
        """
        Check if the toolchain is installed
        
        Args:
            toolchain_path: Path to the toolchain
        
        Returns:
            True if the toolchain is installed, False otherwise
        """
        # Check if the toolchain directory exists
        if not os.path.isdir(toolchain_path):
            return False
        
        # Check if the toolchain contains the necessary files
        env_setup_file = os.path.join(
            toolchain_path,
            'poky-2.1.3',
            'environment-setup-armv7at2hf-neon-poky-linux-gnueabi'
        )
        
        return os.path.isfile(env_setup_file)
    
    def _get_toolchain_path(self) -> str:
        """
        Get the path to the toolchain
        
        Returns:
            Path to the toolchain
        """
        return os.path.expanduser(
            self.direct_config.get('install_path', '~/.parabola-rm-builder/toolchain')
        )
    
    def _install_toolchain(self, toolchain_path: str) -> bool:
        """
        Install the toolchain
        
        Args:
            toolchain_path: Path to install the toolchain
        
        Returns:
            True if the toolchain was installed successfully, False otherwise
        """
        try:
            # Create the toolchain directory
            os.makedirs(toolchain_path, exist_ok=True)
            
            # Download the toolchain
            logger.info("Downloading reMarkable toolchain")
            
            toolchain_url = "https://ipfs.eeems.website/ipfs/Qmdkdeh3bodwDLM9YvPrMoAi6dFYDDCodAnHvjG5voZxiC"
            toolchain_archive = os.path.join(toolchain_path, "toolchain.tar.gz")
            
            # Download the toolchain archive
            subprocess.run(
                ['wget', '-q', toolchain_url, '-O', toolchain_archive],
                check=True
            )
            
            # Extract the toolchain
            logger.info("Extracting toolchain")
            
            subprocess.run(
                ['tar', 'xf', toolchain_archive, '-C', toolchain_path],
                check=True
            )
            
            # Remove the archive
            os.remove(toolchain_archive)
            
            logger.info("Toolchain installed successfully")
            return True
        except Exception as e:
            logger.error("Error installing toolchain: %s", str(e))
            return False
    
    def _setup_env_vars(self, toolchain_path: str) -> None:
        """
        Set up environment variables for the toolchain
        
        Args:
            toolchain_path: Path to the toolchain
        """
        # Source the environment setup script
        env_setup_file = os.path.join(
            toolchain_path,
            'poky-2.1.3',
            'environment-setup-armv7at2hf-neon-poky-linux-gnueabi'
        )
        
        # Parse the environment setup script
        with open(env_setup_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('export '):
                    parts = line[7:].split('=', 1)
                    if len(parts) == 2:
                        key, value = parts
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        self.env_vars[key] = value
        
        # Add environment variables to the current process
        for key, value in self.env_vars.items():
            os.environ[key] = value
    
    def get_build_command(self, command: List[str], cwd: Optional[str] = None) -> List[str]:
        """
        Get the command to run in the cross-compilation environment
        
        Args:
            command: Command to run
            cwd: Working directory
        
        Returns:
            Command to run in the cross-compilation environment
        """
        if self.env_type == 'container':
            return self._get_container_command(command, cwd)
        else:
            return command
    
    def _get_container_command(self, command: List[str], cwd: Optional[str] = None) -> List[str]:
        """
        Get the command to run in the containerized environment
        
        Args:
            command: Command to run
            cwd: Working directory
        
        Returns:
            Command to run in the containerized environment
        """
        container_cmd = [self.container_runtime, 'run', '--rm']
        
        # Add resource limits
        resource_limits = self.container_config.get('resource_limits', {})
        if 'cpu' in resource_limits:
            container_cmd.extend(['--cpus', str(resource_limits['cpu'])])
        if 'memory' in resource_limits:
            container_cmd.extend(['--memory', str(resource_limits['memory'])])
        
        # Add volume mounts
        volume_mounts = self.container_config.get('volume_mounts', [])
        for mount in volume_mounts:
            container_cmd.extend(['-v', mount])
        
        # Add current directory as a volume
        if cwd:
            container_cmd.extend(['-v', f"{os.path.abspath(cwd)}:/workspaces/cwd"])
            container_cmd.extend(['-w', '/workspaces/cwd'])
        
        # Add the image name
        container_cmd.append(self._get_container_image_name())
        
        # Add the command
        container_cmd.extend(['-c', ' '.join(command)])
        
        return container_cmd
    
    def run_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
        """
        Run a command in the cross-compilation environment
        
        Args:
            command: Command to run
            cwd: Working directory
        
        Returns:
            Tuple of (return code, stdout, stderr)
        """
        try:
            cmd = self.get_build_command(command, cwd)
            
            logger.debug("Running command: %s", ' '.join(cmd))
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=os.environ.copy()
            )
            
            stdout, stderr = process.communicate()
            
            return process.returncode, stdout.decode(), stderr.decode()
        except Exception as e:
            logger.error("Error running command: %s", str(e))
            return 1, '', str(e)