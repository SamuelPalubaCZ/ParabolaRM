# Parabola RM Builder Developer Guide

This guide provides information for developers who want to contribute to the Parabola RM Builder project or extend its functionality.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Development Environment](#development-environment)
3. [Adding New Features](#adding-new-features)
4. [Testing](#testing)
5. [Contributing](#contributing)

## Project Structure

The Parabola RM Builder project is organized as follows:

```
parabola-rm-builder/
├── bin/                      # Executable scripts
├── config/                   # Configuration files
│   ├── default.yaml          # Default configuration
│   └── presets/              # Preset configurations
├── docs/                     # Documentation
├── resources/                # Resources
│   ├── assets/               # Assets (splash screens, etc.)
│   ├── patches/              # Patches for bootloader and kernel
│   └── templates/            # Templates
├── src/                      # Source code
│   ├── builders/             # Component builders
│   │   ├── bootloader/       # Bootloader builder
│   │   ├── kernel/           # Kernel builder
│   │   └── partition/        # Partition manager
│   ├── config_manager/       # Configuration management
│   ├── cross_env/            # Cross-compilation environment
│   │   ├── container/        # Container management
│   │   ├── toolchain/        # Toolchain management
│   │   └── shared/           # Shared build scripts
│   ├── executor/             # Installation executor
│   ├── installers/           # Installation components
│   │   ├── desktop/          # Desktop environment configurator
│   │   └── system/           # System installer
│   └── verification/         # Verification system
└── docker/                   # Docker files
    ├── base/                 # Base container image
    ├── toolchain/            # Toolchain container image
    └── build/                # Build container image
```

## Development Environment

### Prerequisites

- Python 3.6 or higher
- Docker (optional, for containerized cross-compilation)
- Git
- A reMarkable tablet for testing (optional)

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/parabola-rm-builder.git
   cd parabola-rm-builder
   ```

2. Make the main executable script executable:
   ```bash
   chmod +x bin/parabola-rm-builder
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Adding New Features

### Adding a New Builder

To add a new builder, create a new module in the `src/builders` directory. The builder should follow the same pattern as the existing builders:

1. Create a new directory for the builder
2. Create a new module with a class that handles the building process
3. Implement the necessary methods for the builder

For example, to add a new builder for a custom component:

```python
# src/builders/custom/custom_builder.py
class CustomBuilder:
    def __init__(self, config, env_manager):
        self.config = config
        self.env_manager = env_manager
        
    def build(self):
        # Implement the build process
        pass
```

### Adding a New Installer

To add a new installer, create a new module in the `src/installers` directory. The installer should follow the same pattern as the existing installers:

1. Create a new directory for the installer
2. Create a new module with a class that handles the installation process
3. Implement the necessary methods for the installer

For example, to add a new installer for a custom component:

```python
# src/installers/custom/custom_installer.py
class CustomInstaller:
    def __init__(self, config, env_manager):
        self.config = config
        self.env_manager = env_manager
        
    def install(self, mount_points):
        # Implement the installation process
        pass
```

### Adding a New Configuration Option

To add a new configuration option, update the following files:

1. `config/default.yaml`: Add the new option with a default value
2. `src/config_manager/config_manager.py`: Update the validation logic if necessary
3. Update the relevant builder or installer to use the new option

### Adding a New Command

To add a new command to the CLI, update the following files:

1. `src/cli.py`: Add the new command to the argument parser and implement the command handler
2. Update the relevant modules to support the new command

## Testing

### Running Tests

To run the tests, use the following command:

```bash
python -m unittest discover -s tests
```

### Adding Tests

To add a new test, create a new module in the `tests` directory. The test should follow the same pattern as the existing tests:

1. Create a new module with a class that inherits from `unittest.TestCase`
2. Implement the necessary test methods

For example, to add a new test for a custom component:

```python
# tests/test_custom.py
import unittest

class TestCustom(unittest.TestCase):
    def test_custom_feature(self):
        # Implement the test
        pass
```

## Contributing

### Submitting a Pull Request

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Run the tests to ensure your changes don't break existing functionality
5. Submit a pull request

### Coding Standards

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write docstrings for all modules, classes, and functions
- Keep functions small and focused on a single task
- Write tests for new functionality

### Documentation

- Update the documentation when adding new features
- Write clear and concise documentation
- Include examples where appropriate
- Keep the documentation up-to-date with the code

### Commit Messages

- Write clear and concise commit messages
- Use the imperative mood (e.g., "Add feature" not "Added feature")
- Reference issues and pull requests where appropriate