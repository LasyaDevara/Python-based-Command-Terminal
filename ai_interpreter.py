#!/usr/bin/env python3
"""
AI-powered natural language command interpreter using Ollama or OpenAI
"""

import ollama
import re
import json
import os
from typing import Dict, List, Tuple, Optional

# Try to import OpenAI, but don't fail if it's not installed
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AICommandInterpreter:
    def __init__(self, model: str = "llama2", use_openai: bool = False, openai_api_key: str = None):
        """
        Initialize the AI command interpreter

        Args:
            model (str): The model to use for interpretation (Ollama model name or OpenAI model)
            use_openai (bool): Whether to use OpenAI instead of Ollama
            openai_api_key (str): OpenAI API key (if not provided, will try to get from environment)
        """
        self.model = model
        self.use_openai = use_openai
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Validate configuration
        if self.use_openai:
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI package not installed. Install with: pip install openai")
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass openai_api_key parameter")
            # Initialize OpenAI client
            openai.api_key = self.openai_api_key
        self.system_prompt = """
You are an AI assistant that converts natural language commands into terminal commands.
You should output only the terminal command(s) in JSON format, without any explanation.

Available commands:
- pwd: Print working directory
- ls [path]: List directory contents
- cd [directory]: Change directory
- mkdir [directory]: Create directory
- touch [file]: Create empty file
- rm [file/folder]: Remove file or directory
- cp [source] [destination]: Copy file/directory
- mv [source] [destination]: Move file/directory
- cat [file]: Display file contents
- edit [file]: Edit file content
- grep [pattern] [file]: Search for pattern in file
- find [path] [name]: Find files by name
- ps: Show running processes
- cpu: Show CPU usage
- mem: Show memory usage
- df: Show disk usage
- date: Show current date and time
- whoami: Show current user
- uname: Show system information
- echo [text]: Print text
- clear: Clear terminal
- history: Show command history

Examples:
- "create a new folder called test" -> {"command": "mkdir test"}
- "create a new file called main.py" -> {"command": "touch main.py"}
- "move file1.txt into the test folder" -> {"command": "mv file1.txt test/"}
- "copy file1.txt to backup.txt" -> {"command": "cp file1.txt backup.txt"}
- "show me the current directory" -> {"command": "pwd"}
- "list all files in the current directory" -> {"command": "ls"}
- "list folders" -> {"command": "ls"}
- "show running processes" -> {"command": "ps"}
- "remove folder test1" -> {"command": "rm test1"}
- "delete file test.txt" -> {"command": "rm test.txt"}
- "what is the CPU usage?" -> {"command": "cpu"}
- "show memory usage" -> {"command": "mem"}
- "how many files in current folder?" -> {"command": "ls"}
- "find all Python files" -> {"command": "find . .py"}
- "search for 'hello' in main.py" -> {"command": "grep hello main.py"}
- "edit the file config.txt" -> {"command": "edit config.txt"}
- "show me the contents of readme.txt" -> {"command": "cat readme.txt"}
- "what time is it?" -> {"command": "date"}
- "who am I?" -> {"command": "whoami"}
- "what system am I running?" -> {"command": "uname"}
- "how much disk space do I have?" -> {"command": "df"}

If multiple commands are needed, return them as a list:
- "create a folder called test and move file1.txt into it" -> {"commands": ["mkdir test", "mv file1.txt test/"]}

Output format: JSON with either "command" (string) or "commands" (array of strings)
"""

    def interpret_command(self, natural_language_input: str) -> Dict[str, str]:
        """
        Convert natural language to terminal command(s)

        Args:
            natural_language_input (str): The natural language command

        Returns:
            dict: Dictionary containing the command(s) to execute
        """
        try:
            # Check for file/folder creation patterns first
            if self._is_file_creation_request(natural_language_input):
                return self._handle_file_creation_request(natural_language_input)
            
            # Create the prompt
            prompt = f"Convert this to terminal command(s): {natural_language_input}"

            if self.use_openai:
                # Use OpenAI
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.1
                )
                response_text = response.choices[0].message.content.strip()
            else:
                # Use Ollama
                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
                response_text = response["message"]["content"].strip()

            # Try to parse as JSON
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                # If not JSON, try to extract command from text
                return self._extract_command_from_text(response_text)

        except Exception as e:
            # Fallback to simple pattern matching if AI fails
            return self._fallback_interpretation(natural_language_input)

    def _extract_command_from_text(self, text: str) -> Dict[str, str]:
        """
        Extract command from AI response text if JSON parsing fails

        Args:
            text (str): The AI response text

        Returns:
            dict: Dictionary containing the command(s)
        """
        # Look for command patterns in the text
        command_patterns = [
            r'`([^`]+)`',  # Commands in backticks
            r'"([^"]+)"',  # Commands in quotes
            r'(\w+\s+[^\n]+)',  # Simple command patterns
        ]

        for pattern in command_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if len(matches) == 1:
                    return {"command": matches[0].strip()}
                else:
                    return {"commands": [match.strip() for match in matches]}

        # If no pattern found, return the whole text as a command
        return {"command": text.strip()}

    def _fallback_interpretation(self, text: str) -> Dict[str, str]:
        """
        Simple fallback interpretation using pattern matching

        Args:
            text (str): The natural language input

        Returns:
            dict: Dictionary containing the interpreted command
        """
        text = text.lower()

        # Simple pattern matching for common commands
        patterns = {
            r'create.*folder.*called (\w+)': 'mkdir {}',
            r'make.*directory.*called (\w+)': 'mkdir {}',
            r'create.*directory.*called (\w+)': 'mkdir {}',
            r'new folder (\w+)': 'mkdir {}',
            r'create.*file.*called (\w+)': 'touch {}',
            r'make.*file.*called (\w+)': 'touch {}',
            r'new file (\w+)': 'touch {}',
            r'list.*files': 'ls',
            r'list.*folders': 'ls',
            r'show.*directory': 'ls',
            r'what.*files.*do.*i.*have': 'ls',
            r'what.*files.*have': 'ls',
            r'what.*files.*are.*here': 'ls',
            r'show.*me.*files': 'ls',
            r'current.*directory': 'pwd',
            r'where.*am.*i': 'pwd',
            r'what.*directory.*am.*i.*using': 'pwd',
            r'go to (\w+)': 'cd {}',
            r'change.*to (\w+)': 'cd {}',
            r'navigate.*to (\w+)': 'cd {}',
            r'show.*processes': 'ps',
            r'running.*processes': 'ps',
            r'cpu.*usage': 'cpu',
            r'memory.*usage': 'mem',
            r'what.*is.*my.*memory.*usage': 'mem',
            r'what.*is.*my.*cpu.*usage': 'cpu',
            r'disk.*usage': 'df',
            r'disk.*space': 'df',
            r'clear.*screen': 'clear',
            r'command.*history': 'history',
            r'move.*file.*(\w+).*to (\w+)': 'mv {} {}',
            r'copy.*file.*(\w+).*to (\w+)': 'cp {} {}',
            r'delete.*file (\w+)': 'rm {}',
            r'remove.*file (\w+)': 'rm {}',
            r'delete.*folder (\w+)': 'rm {}',
            r'remove.*folder (\w+)': 'rm {}',
            r'display.*file (\w+)': 'cat {}',
            r'show.*file (\w+)': 'cat {}',
            r'show.*contents.*of (\w+)': 'cat {}',
            r'edit.*file (\w+)': 'edit {}',
            r'find.*file (\w+)': 'find . {}',
            r'search.*for (\w+)': 'find . {}',
            r'find.*all.*(\w+)': 'find . {}',
            r'grep.*(\w+).*in (\w+)': 'grep {} {}',
            r'search.*for.*(\w+).*in (\w+)': 'grep {} {}',
            r'what.*time': 'date',
            r'current.*time': 'date',
            r'who.*am.*i': 'whoami',
            r'current.*user': 'whoami',
            r'what.*system': 'uname',
            r'system.*info': 'uname',
            r'how.*many.*files': 'ls',
            r'count.*files': 'ls',
        }

        for pattern, command_template in patterns.items():
            match = re.search(pattern, text)
            if match:
                if '{}' in command_template:
                    command = command_template.format(*match.groups())
                else:
                    command = command_template
                return {"command": command}

        # If no pattern matches, return as-is (might be a direct command)
        return {"command": text}
    
    def _is_file_creation_request(self, text: str) -> bool:
        """
        Check if the input is requesting file or folder creation
        
        Args:
            text (str): The natural language input
            
        Returns:
            bool: True if it's a file/folder creation request
        """
        text_lower = text.lower()
        creation_keywords = [
            'create', 'make', 'new', 'build', 'add'
        ]
        file_keywords = [
            'file', 'folder', 'directory', 'document', 'text file', 'python file'
        ]
        
        has_creation = any(keyword in text_lower for keyword in creation_keywords)
        has_file = any(keyword in text_lower for keyword in file_keywords)
        
        return has_creation and has_file
    
    def _handle_file_creation_request(self, text: str) -> Dict[str, str]:
        """
        Handle file/folder creation requests by triggering interactive dialogs
        
        Args:
            text (str): The natural language input
            
        Returns:
            dict: Dictionary containing the command to execute
        """
        text_lower = text.lower()
        
        # Determine if it's a file or folder creation
        if any(keyword in text_lower for keyword in ['folder', 'directory']):
            return {"command": "mkdir"}  # This will trigger the interactive dialog
        else:
            return {"command": "touch"}  # This will trigger the interactive dialog

    def is_available(self) -> bool:
        """
        Check if the AI service is available

        Returns:
            bool: True if the configured AI service is available
        """
        try:
            if self.use_openai:
                # Check if OpenAI is available and API key is set
                return OPENAI_AVAILABLE and bool(self.openai_api_key)
            else:
                # Check if Ollama is available
                ollama.list()
                return True
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        """
        Get list of available models

        Returns:
            list: List of available model names
        """
        try:
            if self.use_openai:
                # Return common OpenAI models
                return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
            else:
                # Return Ollama models
                models = ollama.list()
                return [model["name"] for model in models.get("models", [])]
        except Exception:
            return []
