# Contributing to Parabola RM Builder

Thank you for your interest in contributing to Parabola RM Builder! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Environment](#development-environment)
4. [Coding Standards](#coding-standards)
5. [Submitting Changes](#submitting-changes)
6. [Testing](#testing)
7. [Documentation](#documentation)

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/parabola-rm-builder.git`
3. Set up the development environment (see below)
4. Create a new branch for your changes: `git checkout -b feature/your-feature-name`
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Environment

### Setting Up the Development Environment

1. Run the initialization script:
   ```bash
   ./init_dev_env.sh
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Cross-Compilation Environment

The project supports two approaches for cross-compilation:

1. **Containerized Environment (Default)**:
   ```bash
   ./docker/build_image.sh
   ```

2. **Direct Toolchain**:
   ```bash
   ./src/cross_env/toolchain/installers/install_toolchain.sh
   ```

## Coding Standards

This project follows these coding standards:

- **Python**: PEP 8 style guide
- **Shell Scripts**: Google Shell Style Guide
- **YAML**: 2-space indentation
- **Markdown**: CommonMark specification

We use the following tools to enforce coding standards:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

These tools are configured in the project and can be run using pre-commit hooks.

## Submitting Changes

1. Ensure your code follows the coding standards
2. Write tests for your changes
3. Update documentation as necessary
4. Commit your changes with a descriptive commit message
5. Push your changes to your fork
6. Submit a pull request

### Pull Request Guidelines

- Use a clear and descriptive title
- Include a detailed description of the changes
- Reference any related issues
- Ensure all tests pass
- Include screenshots or examples if applicable

## Testing

### Running Tests

```bash
./run_tests.sh
```

### Writing Tests

- Write tests for all new features and bug fixes
- Follow the existing test structure
- Use descriptive test names
- Aim for high test coverage

## Documentation

- Update documentation for all new features and changes
- Follow the existing documentation style
- Use clear and concise language
- Include examples where appropriate