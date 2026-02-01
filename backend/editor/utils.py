"""
Utility functions for the editor module.
"""
import os
from pathlib import Path

def ensure_directory(path):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)
    return path
