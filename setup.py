#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="parabola-rm-builder",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A configurable builder for Parabola RM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/parabola-rm-builder",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyyaml>=5.1",
        "argparse>=1.4.0",
    ],
    entry_points={
        "console_scripts": [
            "parabola-rm-builder=src.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml", "resources/**/*"],
    },
)