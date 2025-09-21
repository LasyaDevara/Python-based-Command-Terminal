#!/usr/bin/env python3
"""
Helper utilities for the terminal
"""

import os
import shutil

def safe_remove_file(filepath):
    """
    Safely remove a file with error handling
    
    Args:
        filepath (str): Path to the file to remove
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except OSError:
        return False

def safe_remove_directory(dirpath):
    """
    Safely remove a directory with error handling
    
    Args:
        dirpath (str): Path to the directory to remove
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
            return True
        return False
    except OSError:
        return False

def format_output(text, color=None):
    """
    Format output text (placeholder for rich formatting)
    
    Args:
        text (str): Text to format
        color (str): Optional color code
        
    Returns:
        str: Formatted text
    """
    # Placeholder for rich formatting
    return text

def error_message(msg):
    """
    Format an error message
    
    Args:
        msg (str): Error message
        
    Returns:
        str: Formatted error message
    """
    return f"Error: {msg}"
