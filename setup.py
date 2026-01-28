#!/usr/bin/env python3
from setuptools import setup
import os

# Read the main script to use as module
setup(
    name='sr-tui',
    version='1.0.0',
    description='TUI för Sveriges Radio',
    author='Zakenaio',
    scripts=['sr-tui.py'],  # Install as script instead of module
    install_requires=[
        'requests',
        'rich',
    ],
    python_requires='>=3.6',
)
