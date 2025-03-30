# Parabola RM Builder

A configurable builder for Parabola RM, a free and open-source operating system for the reMarkable tablet.

## Overview

Parabola RM Builder is a comprehensive tool that automates the installation of Parabola GNU/Linux-libre on reMarkable tablets. It provides users with configuration options for various aspects of the installation, including partitioning, bootloader settings, kernel options, and desktop environment preferences.

The builder handles the entire installation process, from compiling the bootloader and kernel to partitioning the eMMC storage, installing the Parabola system files, and configuring the desktop environment.

## Features

- **Configurable Installation**: Customize various aspects of the installation through a YAML configuration file.
- **Cross-Compilation Environment**: Supports both containerized and direct toolchain approaches for cross-compilation.
- **Bootloader Building**: Compiles and configures the U-Boot bootloader.
- **Kernel Building**: Compiles and configures the Linux kernel with custom options.
- **Partition Management**: Handles partitioning and formatting of the eMMC storage.
- **System Installation**: Installs the Parabola system files and configures the system.
- **Desktop Environment**: Installs and configures the desktop environment with e-paper optimizations.
- **Installation Verification**: Verifies the installation to ensure everything is working correctly.

## Quick Start

### Using the Direct Scripts

The easiest way to build and install Parabola RM is to use the direct scripts:

```bash
# Build and install everything
./build_and_install.sh --device /dev/mmcblk1

# Or run the steps individually
./download_and_build.sh      # Build the kernel and bootloader
./download_rootfs.sh         # Download the Parabola rootfs
./install_to_device.sh       # Install to the device
./configure_desktop.sh       # Configure the desktop environment
```

### Using the Python Framework

For more control and customization, you can use the Python framework:

1. **Initialize a configuration**:
   ```bash
   ./run_builder.sh init -o my-config.yaml
   ```

2. **Set up the cross-compilation environment**:
   ```bash
   ./run_builder.sh env --setup -c my-config.yaml
   ```

3. **Build components**:
   ```bash
   ./run_builder.sh build --all -c my-config.yaml
   ```

4. **Install Parabola RM**:
   ```bash
   ./run_builder.sh install --device /dev/mmcblk1 -c my-config.yaml
   ```

## Installation

### Prerequisites

- Python 3.6 or higher
- Docker (optional, for containerized cross-compilation)
- Git
- USB connection to the reMarkable tablet

### Installing from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/parabola-rm-builder.git
   cd parabola-rm-builder
   ```

2. Make the main executable script executable:
   ```bash
   chmod +x bin/parabola-rm-builder
   ```

3. Add the bin directory to your PATH (optional):
   ```bash
   export PATH="$PATH:$(pwd)/bin"
   ```

### Installing with pip

```bash
pip install parabola-rm-builder
```

## Configuration

Parabola RM Builder uses a YAML configuration file to customize the installation. You can create a new configuration file with the `init` command:

```bash
./run_builder.sh init -o my-config.yaml
```

This will create a new configuration file with default settings. You can then edit this file to customize your installation.

### Configuration Options

The configuration file is divided into several sections:

- **Cross-Compilation Environment**: Configure the cross-compilation environment, including whether to use a containerized environment or a direct toolchain.
- **Hardware Configuration**: Configure the target hardware, including the tablet model and storage options.
- **Partition Configuration**: Configure the partition layout and filesystem options.
- **Bootloader Configuration**: Configure the bootloader, including boot parameters and splash screen.
- **Kernel Configuration**: Configure the kernel, including driver options and hardware support.
- **System Configuration**: Configure the system, including network settings and system services.
- **Desktop Environment Configuration**: Configure the desktop environment, including UI customization and input methods.

For a complete list of configuration options, see the [Configuration Reference](docs/configuration_reference.md).

### Using Preset Configurations

Parabola RM Builder comes with several preset configurations that you can use as a starting point:

- **minimal.yaml**: A minimal configuration for a basic installation.

To use a preset configuration, copy it to your working directory and customize it as needed:

```bash
cp config/presets/minimal.yaml my-config.yaml
```

## Development

For development, use the provided scripts:

1. **Set up development environment**:
   ```bash
   ./init_dev_env.sh
   ```

2. **Run tests**:
   ```bash
   ./run_tests.sh
   ```

3. **Build Docker image for cross-compilation**:
   ```bash
   ./docker/build_image.sh
   ```

4. **Create a test image for testing**:
   ```bash
   ./create_test_image.sh
   ```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Parabola GNU/Linux-libre](https://www.parabola.nu/)
- [reMarkable](https://remarkable.com/)
- [Davis Remmel](http://www.davisr.me/projects/parabola-rm/) - Original creator of Parabola-rM