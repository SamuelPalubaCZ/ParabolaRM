#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for the Cross-Compilation Environment Manager
"""

import os
import sys
import unittest
import tempfile
import yaml
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cross_env.env_manager import CrossEnvManager

class TestCrossEnvManager(unittest.TestCase):
    """
    Tests for the Cross-Compilation Environment Manager
    """
    
    def setUp(self):
        """
        Set up the test
        """
        # Create a test configuration
        self.test_config = {
            'cross_compilation': {
                'environment_type': 'container',
                'toolchain_version': 'test',
                'container': {
                    'base_image': 'test:latest',
                    'resource_limits': {
                        'cpu': 2,
                        'memory': '2g'
                    },
                    'volume_mounts': [
                        'source:/workspaces/source',
                        'output:/workspaces/output'
                    ]
                },
                'direct': {
                    'install_path': '/tmp/toolchain',
                    'use_system_package_manager': True
                },
                'build': {
                    'parallel_jobs': 2,
                    'use_ccache': True,
                    'cache_dir': '/tmp/cache'
                }
            }
        }
    
    def test_init(self):
        """
        Test initialization of the Cross-Compilation Environment Manager
        """
        # Create a Cross-Compilation Environment Manager
        env_manager = CrossEnvManager(self.test_config)
        
        # Check that the configuration was loaded correctly
        self.assertEqual(env_manager.env_type, 'container')
        self.assertEqual(env_manager.toolchain_version, 'test')
        self.assertEqual(env_manager.container_config, self.test_config['cross_compilation']['container'])
        self.assertEqual(env_manager.build_config, self.test_config['cross_compilation']['build'])
    
    @patch('subprocess.run')
    def test_check_container_runtime_docker(self, mock_run):
        """
        Test checking for Docker container runtime
        """
        # Mock the subprocess.run function to return success for Docker
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b'Docker version 20.10.7, build f0df350'
        mock_run.return_value = mock_process
        
        # Create a Cross-Compilation Environment Manager
        env_manager = CrossEnvManager(self.test_config)
        
        # Check for container runtime
        result = env_manager._check_container_runtime()
        
        # Check that Docker was found
        self.assertTrue(result)
        self.assertEqual(env_manager.container_runtime, 'docker')
        
        # Check that subprocess.run was called with the correct arguments
        mock_run.assert_called_once_with(
            ['docker', '--version'],
            stdout=-1,
            stderr=-1,
            check=False
        )
    
    @patch('subprocess.run')
    def test_check_container_runtime_podman(self, mock_run):
        """
        Test checking for Podman container runtime
        """
        # Mock the subprocess.run function to return failure for Docker and success for Podman
        mock_docker_process = MagicMock()
        mock_docker_process.returncode = 1
        mock_podman_process = MagicMock()
        mock_podman_process.returncode = 0
        mock_podman_process.stdout = b'podman version 3.0.1'
        mock_run.side_effect = [mock_docker_process, mock_podman_process]
        
        # Create a Cross-Compilation Environment Manager
        env_manager = CrossEnvManager(self.test_config)
        
        # Check for container runtime
        result = env_manager._check_container_runtime()
        
        # Check that Podman was found
        self.assertTrue(result)
        self.assertEqual(env_manager.container_runtime, 'podman')
        
        # Check that subprocess.run was called with the correct arguments
        mock_run.assert_any_call(
            ['docker', '--version'],
            stdout=-1,
            stderr=-1,
            check=False
        )
        mock_run.assert_any_call(
            ['podman', '--version'],
            stdout=-1,
            stderr=-1,
            check=False
        )
    
    @patch('subprocess.run')
    def test_check_container_runtime_none(self, mock_run):
        """
        Test checking for container runtime when none is available
        """
        # Mock the subprocess.run function to return failure for both Docker and Podman
        mock_docker_process = MagicMock()
        mock_docker_process.returncode = 1
        mock_podman_process = MagicMock()
        mock_podman_process.returncode = 1
        mock_run.side_effect = [mock_docker_process, mock_podman_process]
        
        # Create a Cross-Compilation Environment Manager
        env_manager = CrossEnvManager(self.test_config)
        
        # Check for container runtime
        result = env_manager._check_container_runtime()
        
        # Check that no container runtime was found
        self.assertFalse(result)
        
        # Check that subprocess.run was called with the correct arguments
        mock_run.assert_any_call(
            ['docker', '--version'],
            stdout=-1,
            stderr=-1,
            check=False
        )
        mock_run.assert_any_call(
            ['podman', '--version'],
            stdout=-1,
            stderr=-1,
            check=False
        )
    
    @patch('os.path.isdir')
    @patch('os.path.isfile')
    def test_check_toolchain(self, mock_isfile, mock_isdir):
        """
        Test checking for the toolchain
        """
        # Mock the os.path.isdir and os.path.isfile functions
        mock_isdir.return_value = True
        mock_isfile.return_value = True
        
        # Create a Cross-Compilation Environment Manager
        env_manager = CrossEnvManager(self.test_config)
        
        # Check for the toolchain
        result = env_manager._check_toolchain('/tmp/toolchain')
        
        # Check that the toolchain was found
        self.assertTrue(result)
        
        # Check that os.path.isdir and os.path.isfile were called with the correct arguments
        mock_isdir.assert_called_once_with('/tmp/toolchain')
        mock_isfile.assert_called_once_with('/tmp/toolchain/poky-2.1.3/environment-setup-armv7at2hf-neon-poky-linux-gnueabi')
    
    @patch('os.path.isdir')
    @patch('os.path.isfile')
    def test_check_toolchain_not_found(self, mock_isfile, mock_isdir):
        """
        Test checking for the toolchain when it is not found
        """
        # Mock the os.path.isdir and os.path.isfile functions
        mock_isdir.return_value = True
        mock_isfile.return_value = False
        
        # Create a Cross-Compilation Environment Manager
        env_manager = CrossEnvManager(self.test_config)
        
        # Check for the toolchain
        result = env_manager._check_toolchain('/tmp/toolchain')
        
        # Check that the toolchain was not found
        self.assertFalse(result)
        
        # Check that os.path.isdir and os.path.isfile were called with the correct arguments
        mock_isdir.assert_called_once_with('/tmp/toolchain')
        mock_isfile.assert_called_once_with('/tmp/toolchain/poky-2.1.3/environment-setup-armv7at2hf-neon-poky-linux-gnueabi')
    
    def test_get_container_command(self):
        """
        Test getting a container command
        """
        # Create a Cross-Compilation Environment Manager
        env_manager = CrossEnvManager(self.test_config)
        env_manager.container_runtime = 'docker'
        
        # Get a container command
        command = ['make', '-j2']
        container_command = env_manager._get_container_command(command, '/tmp/workdir')
        
        # Check that the container command is correct
        self.assertEqual(container_command[0], 'docker')
        self.assertEqual(container_command[1], 'run')
        self.assertEqual(container_command[2], '--rm')
        self.assertIn('--cpus', container_command)
        self.assertIn('2', container_command)
        self.assertIn('--memory', container_command)
        self.assertIn('2g', container_command)
        self.assertIn('-v', container_command)
        self.assertIn('source:/workspaces/source', container_command)
        self.assertIn('-v', container_command)
        self.assertIn('output:/workspaces/output', container_command)
        self.assertIn('-v', container_command)
        self.assertIn('/tmp/workdir:/workspaces/cwd', container_command)
        self.assertIn('-w', container_command)
        self.assertIn('/workspaces/cwd', container_command)
        self.assertIn('parabola-rm-builder-toolchain:test', container_command)
        self.assertIn('-c', container_command)
        self.assertIn('make -j2', container_command)

if __name__ == '__main__':
    unittest.main()