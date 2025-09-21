#!/usr/bin/env python3
"""
Command history storage for terminal sessions
"""

import os
import json

def load_history(session_id):
    """
    Load command history for a session
    
    Args:
        session_id (str): The session ID
        
    Returns:
        list: List of commands in history
    """
    session_file = f"data/sessions/{session_id}.json"
    try:
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                return json.load(f)
        else:
            # Return empty list if no history file exists
            return []
    except (json.JSONDecodeError, IOError):
        # Return empty list if there's an error reading the file
        return []

def save_history(session_id, commands):
    """
    Save command history for a session
    
    Args:
        session_id (str): The session ID
        commands (list): List of commands to save
    """
    session_file = f"data/sessions/{session_id}.json"
    try:
        with open(session_file, 'w') as f:
            json.dump(commands, f)
    except IOError:
        # Silently fail if we can't save history
        pass

def add_command(session_id, command):
    """
    Add a command to the history for a session
    
    Args:
        session_id (str): The session ID
        command (str): The command to add
    """
    history = load_history(session_id)
    history.append(command)
    save_history(session_id, history)
