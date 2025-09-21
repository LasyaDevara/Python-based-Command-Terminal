#!/usr/bin/env python3
"""
Smart command parser that distinguishes between terminal commands and natural language
"""

import re
from typing import Tuple, Optional, List

class CommandParser:
    def __init__(self):
        """Initialize the command parser"""
        # List of known terminal commands
        self.terminal_commands = {
            'pwd', 'ls', 'cd', 'mkdir', 'touch', 'rm', 'cp', 'mv', 'cat', 'edit',
            'grep', 'find', 'ps', 'cpu', 'mem', 'df', 'date', 'whoami', 'uname',
            'echo', 'clear', 'history', 'help', 'exit', 'newterm', 'sessions',
            'switch', 'chat', 'ai'
        }
        
        # Natural language indicators
        self.natural_language_indicators = [
            r'\b(create|make|new|build)\b',
            r'\b(show|display|list|find|search)\b',
            r'\b(move|copy|delete|remove)\b',
            r'\b(what|how|where|when|why)\b',
            r'\b(can you|could you|please)\b',
            r'\b(folder|directory|file)\b',
            r'\b(usage|memory|cpu|disk)\b',
            r'\b(processes|running|current)\b',
            r'\b(contents|inside|within)\b',
            r'\b(edit|modify|change)\b',
            r'\b(time|date|user|system)\b',
            r'\b(space|available|free)\b'
        ]
        
        # Compile regex patterns for efficiency
        self.nl_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.natural_language_indicators]

    def parse_input(self, user_input: str) -> Tuple[str, str, bool]:
        """
        Parse user input to determine if it's a terminal command or natural language
        
        Args:
            user_input (str): The user's input
            
        Returns:
            Tuple[str, str, bool]: (command_type, input, is_natural_language)
        """
        user_input = user_input.strip()
        
        if not user_input:
            return "empty", user_input, False
        
        # Split into words
        words = user_input.split()
        first_word = words[0].lower()
        
        # Check if it's a direct terminal command
        if first_word in self.terminal_commands:
            return "terminal", user_input, False
        
        # Check for natural language patterns
        is_natural_language = self._is_natural_language(user_input)
        
        if is_natural_language:
            return "natural_language", user_input, True
        
        # Check if it might be a shell command (contains special characters)
        if self._is_shell_command(user_input):
            return "shell", user_input, False
        
        # Default to natural language if unclear
        return "natural_language", user_input, True

    def _is_natural_language(self, text: str) -> bool:
        """
        Check if the input appears to be natural language
        
        Args:
            text (str): The input text
            
        Returns:
            bool: True if it appears to be natural language
        """
        text_lower = text.lower()
        
        # Check for natural language patterns
        for pattern in self.nl_patterns:
            if pattern.search(text_lower):
                return True
        
        # Check for question marks or conversational words
        if '?' in text or any(word in text_lower for word in ['please', 'can', 'could', 'would', 'should']):
            return True
        
        # Check for multi-word phrases that are likely natural language
        words = text.split()
        if len(words) > 2:
            # If it's a long phrase and doesn't start with a known command, likely natural language
            if words[0].lower() not in self.terminal_commands:
                return True
        
        return False

    def _is_shell_command(self, text: str) -> bool:
        """
        Check if the input appears to be a shell command
        
        Args:
            text (str): The input text
            
        Returns:
            bool: True if it appears to be a shell command
        """
        # Check for shell-specific characters
        shell_indicators = ['|', '>', '<', '&', ';', '&&', '||', '$', '~', '`']
        
        for indicator in shell_indicators:
            if indicator in text:
                return True
        
        # Check for file paths (Windows and Unix)
        if re.search(r'[a-zA-Z]:\\', text) or re.search(r'/[a-zA-Z]', text):
            return True
        
        # Check for environment variables
        if re.search(r'\$[A-Za-z_][A-Za-z0-9_]*', text):
            return True
        
        return False

    def get_command_suggestions(self, partial_input: str) -> List[str]:
        """
        Get command suggestions based on partial input
        
        Args:
            partial_input (str): Partial command input
            
        Returns:
            List[str]: List of suggested commands
        """
        partial_lower = partial_input.lower()
        suggestions = []
        
        # Find commands that start with the partial input
        for cmd in self.terminal_commands:
            if cmd.startswith(partial_lower):
                suggestions.append(cmd)
        
        # Sort by length (shorter matches first)
        suggestions.sort(key=len)
        
        return suggestions[:10]  # Return top 10 suggestions

    def is_help_request(self, text: str) -> bool:
        """
        Check if the input is asking for help
        
        Args:
            text (str): The input text
            
        Returns:
            bool: True if it's a help request
        """
        help_indicators = [
            'help', '?', 'what can', 'how do', 'commands', 'available',
            'show me', 'tell me', 'explain', 'guide', 'tutorial'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in help_indicators)

    def extract_file_operations(self, text: str) -> Optional[dict]:
        """
        Extract file operation details from natural language
        
        Args:
            text (str): Natural language input
            
        Returns:
            Optional[dict]: Extracted operation details or None
        """
        text_lower = text.lower()
        
        # File creation patterns
        create_patterns = [
            r'create.*(?:file|document).*called\s+([^\s]+)',
            r'make.*(?:file|document).*called\s+([^\s]+)',
            r'new\s+(?:file|document)\s+([^\s]+)',
            r'create.*folder.*called\s+([^\s]+)',
            r'make.*folder.*called\s+([^\s]+)',
            r'new\s+folder\s+([^\s]+)'
        ]
        
        for pattern in create_patterns:
            match = re.search(pattern, text_lower)
            if match:
                filename = match.group(1)
                is_folder = 'folder' in pattern or 'directory' in pattern
                return {
                    'operation': 'create',
                    'target': filename,
                    'is_folder': is_folder
                }
        
        # File movement patterns
        move_patterns = [
            r'move\s+([^\s]+)\s+to\s+([^\s]+)',
            r'copy\s+([^\s]+)\s+to\s+([^\s]+)',
            r'rename\s+([^\s]+)\s+to\s+([^\s]+)'
        ]
        
        for pattern in move_patterns:
            match = re.search(pattern, text_lower)
            if match:
                source = match.group(1)
                destination = match.group(2)
                operation = 'move' if 'move' in pattern else 'copy' if 'copy' in pattern else 'rename'
                return {
                    'operation': operation,
                    'source': source,
                    'destination': destination
                }
        
        return None

