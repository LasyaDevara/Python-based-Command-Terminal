#!/usr/bin/env python3
"""
Enhanced command history with auto-completion and fuzzy search
"""

import os
import json
from typing import List, Dict, Optional, Tuple
from fuzzywuzzy import process, fuzz
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings

class CommandCompleter(Completer):
    def __init__(self, history_manager):
        self.history_manager = history_manager

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        commands = self.history_manager.get_all_commands()

        # Add built-in commands
        builtin_commands = [
            'pwd', 'ls', 'cd', 'mkdir', 'rm', 'rmdir', 'cp', 'mv',
            'cat', 'grep', 'find', 'ps', 'cpu', 'mem', 'echo',
            'clear', 'history', 'help', 'exit', 'newterm', 'sessions',
            'switch', 'chat', 'ai'
        ]

        all_suggestions = commands + builtin_commands

        # Fuzzy match
        matches = process.extract(word, all_suggestions, limit=10, scorer=fuzz.token_sort_ratio)

        for match, score in matches:
            if score > 50:  # Only show reasonably good matches
                yield Completion(match, start_position=-len(word))

class EnhancedHistoryManager:
    def __init__(self, sessions_dir: str = "data/sessions"):
        """
        Initialize enhanced history manager

        Args:
            sessions_dir (str): Directory containing session history files
        """
        self.sessions_dir = sessions_dir
        self.current_session_commands = []
        self.all_commands_cache = None
        self.cache_timestamp = 0

    def load_session_history(self, session_id: str) -> List[str]:
        """
        Load command history for a specific session

        Args:
            session_id (str): The session ID

        Returns:
            list: List of commands from the session
        """
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        try:
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    return json.load(f)
            else:
                return []
        except (json.JSONDecodeError, IOError):
            return []

    def save_session_history(self, session_id: str, commands: List[str]):
        """
        Save command history for a session

        Args:
            session_id (str): The session ID
            commands (list): List of commands to save
        """
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        try:
            os.makedirs(os.path.dirname(session_file), exist_ok=True)
            with open(session_file, 'w') as f:
                json.dump(commands, f)
        except IOError:
            pass

    def add_command(self, session_id: str, command: str):
        """
        Add a command to the history

        Args:
            session_id (str): The session ID
            command (str): The command to add
        """
        # Load current history
        history = self.load_session_history(session_id)

        # Add new command (avoid duplicates)
        if not history or history[-1] != command:
            history.append(command)

        # Save updated history
        self.save_session_history(session_id, history)

        # Update current session cache
        if not self.current_session_commands or self.current_session_commands[-1] != command:
            self.current_session_commands.append(command)

        # Clear all commands cache
        self.all_commands_cache = None

    def get_session_history(self, session_id: str) -> List[str]:
        """
        Get command history for a session

        Args:
            session_id (str): The session ID

        Returns:
            list: List of commands from the session
        """
        return self.load_session_history(session_id)

    def get_all_commands(self) -> List[str]:
        """
        Get all commands from all sessions (cached)

        Returns:
            list: List of all unique commands
        """
        # Simple caching to avoid reading files repeatedly
        current_time = os.path.getmtime(self.sessions_dir) if os.path.exists(self.sessions_dir) else 0

        if self.all_commands_cache is None or current_time > self.cache_timestamp:
            all_commands = set()

            # Get all session files
            if os.path.exists(self.sessions_dir):
                for filename in os.listdir(self.sessions_dir):
                    if filename.endswith('.json'):
                        session_commands = self.load_session_history(filename[:-5])  # Remove .json
                        all_commands.update(session_commands)

            self.all_commands_cache = list(all_commands)
            self.cache_timestamp = current_time

        return self.all_commands_cache

    def search_commands(self, query: str, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Search commands using fuzzy matching

        Args:
            query (str): Search query
            limit (int): Maximum number of results

        Returns:
            list: List of tuples (command, score)
        """
        commands = self.get_all_commands()
        matches = process.extract(query, commands, limit=limit, scorer=fuzz.token_sort_ratio)
        return matches

    def get_similar_commands(self, partial_command: str, limit: int = 5) -> List[str]:
        """
        Get commands similar to the partial command

        Args:
            partial_command (str): Partial command to match
            limit (int): Maximum number of suggestions

        Returns:
            list: List of similar commands
        """
        commands = self.get_all_commands()
        matches = process.extract(partial_command, commands, limit=limit, scorer=fuzz.partial_ratio)
        return [match[0] for match in matches if match[1] > 60]  # Only good matches

    def get_recent_commands(self, limit: int = 10) -> List[str]:
        """
        Get most recent commands

        Args:
            limit (int): Maximum number of commands

        Returns:
            list: List of recent commands
        """
        return self.current_session_commands[-limit:] if self.current_session_commands else []

    def create_prompt_session(self, session_id: str) -> PromptSession:
        """
        Create a prompt session with auto-completion and history

        Args:
            session_id (str): The session ID

        Returns:
            PromptSession: Configured prompt session
        """
        # Create history file for this session
        history_file = os.path.join(self.sessions_dir, f"{session_id}_prompt.txt")
        os.makedirs(os.path.dirname(history_file), exist_ok=True)

        # Create completer
        completer = CommandCompleter(self)

        # Create prompt session
        session = PromptSession(
            history=FileHistory(history_file),
            completer=completer,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
            search_ignore_case=True
        )

        return session

    def get_command_stats(self) -> Dict[str, int]:
        """
        Get statistics about command usage

        Returns:
            dict: Dictionary with command usage statistics
        """
        all_commands = self.get_all_commands()
        stats = {}

        for cmd in all_commands:
            parts = cmd.split()
            if parts:
                base_cmd = parts[0]
                stats[base_cmd] = stats.get(base_cmd, 0) + 1

        return stats
