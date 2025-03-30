# Parabola RM Builder User Guide

This guide provides detailed instructions for using the Parabola RM Builder to install Parabola GNU/Linux-libre on your reMarkable tablet.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Building Components](#building-components)
6. [Installing Parabola RM](#installing-parabola-rm)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

## Introduction

Parabola RM Builder is a comprehensive tool that automates the installation of Parabola GNU/Linux-libre on reMarkable tablets. It provides users with configuration options for various aspects of the installation, including partitioning, bootloader settings, kernel options, and desktop environment preferences.

The builder handles the entire installation process, from compiling the bootloader and kernel to partitioning the eMMC storage, installing the Parabola system files, and configuring the desktop environment.

## Prerequisites

Before using Parabola RM Builder, ensure you have the following:

- A reMarkable tablet (RM1 or RM2)
- A computer running Linux, macOS, or Windows with WSL
- Python 3.6 or higher
- Docker (optional, for containerized cross-compilation)
- Git
- USB connection to the reMarkable tablet
- Basic knowledge of Linux command line

## Installation

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
parabola-rm-builder init -o my-config.yaml
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

For a complete list of configuration options, see the [Configuration Reference](configuration_reference.md).

### Using Preset Configurations

Parabola RM Builder comes with several preset configurations that you can use as a starting point:

- **minimal.yaml**: A minimal configuration for a basic installation.
- **desktop.yaml**: A configuration for a desktop-oriented installation.
- **developer.yaml**: A configuration for a developer-oriented installation.

To use a preset configuration, copy it to your working directory and customize it as needed:

```bash
cp config/presets/minimal.yaml my-config.yaml
```

## Building Components

Before installing Parabola RM, you need to build the necessary components. You can build all components at once or build them individually.

### Building All Components

```bash
parabola-rm-builder build --all -c my-config.yaml
```

### Building Individual Components

```bash
parabola-rm-builder build --bootloader -c my-config.yaml
parabola-rm-builder build --kernel -c my-config.yaml
```

## Installing Parabola RM

Once you have built the necessary components, you can install Parabola RM to your reMarkable tablet.

### Preparing the Tablet

1. Put your tablet into recovery mode:
   - Turn off the tablet
   - Hold the middle button while pressing the power button
   - Continue holding the middle button for 5 seconds while releasing the power button

2. Connect the tablet to your computer via USB

### Installing Parabola RM

```bash
parabola-rm-builder install --device /dev/mmcblk1 -c my-config.yaml
```

Replace `/dev/mmcblk1` with the device path of your tablet's eMMC storage. You can find this by running `lsblk` after connecting the tablet.

## Troubleshooting

### Common Issues

#### Failed to Build Components

If you encounter issues building components, try the following:

- Ensure you have the necessary dependencies installed
- Check the logs for specific error messages
- Try using a containerized environment with `cross_compilation.environment_type: container`

#### Failed to Install Parabola RM

If you encounter issues installing Parabola RM, try the following:

- Ensure the tablet is in recovery mode
- Check the device path is correct
- Check the logs for specific error messages

### Getting Help

If you encounter issues that are not covered in this guide, please open an issue on the GitHub repository.

## Advanced Usage

### Customizing the Bootloader

You can customize the bootloader by modifying the `bootloader` section in the configuration file. For example, you can change the boot parameters or use a custom splash screen.

### Customizing the Kernel

You can customize the kernel by modifying the `kernel` section in the configuration file. For example, you can enable or disable specific drivers or hardware support.

### Customizing the Desktop Environment

You can customize the desktop environment by modifying the `desktop` section in the configuration file. For example, you can change the theme, font settings, or input methods.

### Using a Custom Toolchain

If you have a custom toolchain, you can use it by setting `cross_compilation.environment_type` to `direct` and configuring the `cross_compilation.direct` section in the configuration file.

### Using a Custom Rootfs

If you have a custom rootfs, you can use it by placing it in the `resources/rootfs` directory and setting `system.rootfs.use_custom` to `true` in the configuration file.