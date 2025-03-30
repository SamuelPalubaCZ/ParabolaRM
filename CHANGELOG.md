# Changelog

All notable changes to the Parabola RM Builder project will be documented in this file.

## [0.1.0] - 2025-03-30

### Added

#### Core Framework
- Initial implementation of the configuration management system
- Implementation of the cross-compilation environment manager
- Implementation of the bootloader builder (U-Boot)
- Implementation of the kernel builder (Linux)
- Implementation of the partition manager
- Implementation of the system installer
- Implementation of the desktop environment configurator (Xfce)
- Implementation of the installation executor
- Implementation of the installation verifier
- Implementation of the command-line interface

#### Direct Shell Scripts
- `download_and_build.sh`: Script to download and build the kernel and bootloader
- `download_rootfs.sh`: Script to download the Parabola rootfs
- `install_to_device.sh`: Script to install to the device
- `configure_desktop.sh`: Script to configure the desktop environment
- `build_and_install.sh`: Main script that runs all steps in sequence

#### Configuration
- Default configuration file (`config/default.yaml`)
- Minimal configuration preset (`config/presets/minimal.yaml`)

#### Development Tools
- Test runner script (`tests/run_tests.py`)
- Development environment setup script (`init_dev_env.sh`)
- Docker image builder script (`docker/build_image.sh`)
- Release package creator script (`create_release.sh`)
- Test image creator script (`create_test_image.sh`)

#### Documentation
- README.md with project overview, features, and usage instructions
- User guide (`docs/user_guide.md`)
- Developer guide (`docs/developer_guide.md`)
- Contributing guidelines (`CONTRIBUTING.md`)

#### Testing
- Basic test framework
- Tests for the configuration manager
- Tests for the cross-compilation environment manager
- Tests for the CLI interface
- Tests for the installation executor

#### Miscellaneous
- License file (GPL-3.0)
- .gitignore file
- Setup script for Python package installation
- MANIFEST.in file for package data inclusion
- Requirements file for dependencies
- Configuration files for development tools (pytest, flake8, black, mypy, etc.)