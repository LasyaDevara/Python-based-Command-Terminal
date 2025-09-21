#!/usr/bin/env python3
"""
Unified processor that automatically detects and handles commands, natural language, and chat
"""

import os
import re
from typing import Tuple, Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from command_parser import CommandParser
from ai_interpreter import AICommandInterpreter
from terminal import run_command
from session_manager import SessionManager

class UnifiedProcessor:
    def __init__(self, session_manager: SessionManager, use_openai: bool = False, openai_api_key: str = None):
        """Initialize the unified processor"""
        self.console = Console()
        self.session_manager = session_manager
        self.command_parser = CommandParser()
        self.ai_interpreter = AICommandInterpreter(use_openai=use_openai, openai_api_key=openai_api_key)
        self.chat_context = []  # Store chat context
        self.conversation_mode = False
        
        # Chat indicators
        self.chat_keywords = [
            'hello', 'hi', 'hey', 'thanks', 'thank you', 'please', 'help me',
            'can you', 'could you', 'would you', 'what is', 'how do', 'why',
            'explain', 'tell me', 'show me', 'i need', 'i want', 'i am',
            'my name is', 'i am working on', 'i have a problem', 'i need help'
        ]
        
        # Command patterns that should be executed directly
        self.direct_command_patterns = [
            r'^cd\s+',  # cd command
            r'^ls\s*',  # ls command
            r'^pwd\s*',  # pwd command
            r'^exit\s*',  # exit command
            r'^help\s*',  # help command
            r'^clear\s*',  # clear command
            r'^mkdir\s+',  # mkdir command
            r'^touch\s+',  # touch command
            r'^rm\s+',  # rm command
            r'^cp\s+',  # cp command
            r'^mv\s+',  # mv command
            r'^cat\s+',  # cat command
            r'^edit\s+',  # edit command
            r'^find\s+',  # find command
            r'^grep\s+',  # grep command
            r'^ps\s*',  # ps command
            r'^cpu\s*',  # cpu command
            r'^mem\s*',  # mem command
            r'^df\s*',  # df command
            r'^date\s*',  # date command
            r'^whoami\s*',  # whoami command
            r'^uname\s*',  # uname command
            r'^echo\s+',  # echo command
            r'^history\s*',  # history command
            r'^stats\s*',  # stats command
            r'^newterm\s*',  # newterm command
            r'^sessions\s*',  # sessions command
            r'^switch\s+',  # switch command
        ]
    
    def process_input(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """
        Process any input and determine the best way to handle it
        
        Args:
            user_input (str): The user's input
            session_id (str): Current session ID
            
        Returns:
            Dict containing the result and metadata
        """
        user_input = user_input.strip()
        
        if not user_input:
            return {"type": "empty", "result": "", "message": ""}
        
        # Check for conversation mode toggle
        if self._is_conversation_toggle(user_input) or self._classify_input(user_input) == "conversation_toggle":
            return self._toggle_conversation_mode()
        
        # Check if we're in conversation mode
        if self.conversation_mode:
            return self._handle_conversation_input(user_input, session_id)
        
        # Determine input type and process accordingly
        input_type = self._classify_input(user_input)
        
        if input_type == "direct_command":
            return self._handle_direct_command(user_input, session_id)
        elif input_type == "simple_folder_creation":
            return self._handle_simple_folder_creation(user_input, session_id)
        elif input_type == "simple_file_creation":
            return self._handle_simple_file_creation(user_input, session_id)
        elif input_type == "file_operation":
            return self._handle_file_operation(user_input, session_id)
        elif input_type == "system_query":
            return self._handle_system_query(user_input, session_id)
        elif input_type == "chat":
            return self._handle_chat_input(user_input, session_id)
        elif input_type == "natural_language":
            return self._handle_natural_language(user_input, session_id)
        else:
            return self._handle_unknown_input(user_input, session_id)
    
    def _is_conversation_toggle(self, user_input: str) -> bool:
        """Check if user wants to toggle conversation mode"""
        toggle_commands = ['chat', 'conversation', 'talk', 'converse']
        return user_input.lower() in toggle_commands
    
    def _toggle_conversation_mode(self) -> Dict[str, Any]:
        """Toggle conversation mode on/off"""
        self.conversation_mode = not self.conversation_mode
        if self.conversation_mode:
            self.chat_context = []
            return {
                "type": "conversation_toggle",
                "result": "Conversation mode enabled. I'm here to help!",
                "message": "You can now have a natural conversation with me.",
                "conversation_mode": True
            }
        else:
            return {
                "type": "conversation_toggle", 
                "result": "Conversation mode disabled.",
                "message": "Back to command mode.",
                "conversation_mode": False
            }
    
    def _classify_input(self, user_input: str) -> str:
        """Classify the type of input"""
        user_input_lower = user_input.lower()
        
        # Check for conversation toggles first
        if user_input.lower() in ['chat', 'conversation', 'talk', 'converse']:
            return "conversation_toggle"
        
        # Check for single word commands that are known terminal commands
        if len(user_input.split()) == 1 and user_input in ['ls', 'pwd', 'ps', 'cpu', 'mem', 'df', 'date', 'whoami', 'uname', 'clear', 'exit', 'history', 'stats', 'newterm', 'sessions']:
            return "direct_command"
        
        # Check for specific command patterns (only for single words or specific formats)
        for pattern in self.direct_command_patterns:
            if re.match(pattern, user_input):
                return "direct_command"
        
        # Check for simple folder/file creation first (fast path - highest priority)
        if self._is_simple_folder_creation(user_input_lower):
            return "simple_folder_creation"
        elif self._is_simple_file_creation(user_input_lower):
            return "simple_file_creation"
        
        # Check for system queries (after simple operations to avoid conflicts)
        if self._is_system_query(user_input_lower):
            return "system_query"
        
        # Check for file operations
        if self._is_file_operation(user_input_lower):
            return "file_operation"
        
        # Check for natural language commands (expanded to catch more patterns)
        if self._is_natural_language(user_input_lower):
            return "natural_language"
        
        # Check for chat indicators (moved after other checks to avoid false positives)
        if self._is_chat_input(user_input_lower):
            return "chat"
        
        # Default to unknown
        return "unknown"
    
    def _is_file_operation(self, text: str) -> bool:
        """Check if input is about file operations"""
        file_keywords = [
            'create', 'make', 'new', 'file', 'folder', 'directory',
            'delete', 'remove', 'copy', 'move', 'rename', 'edit',
            'open', 'read', 'write', 'save', 'find', 'search'
        ]
        return any(keyword in text for keyword in file_keywords)
    
    def _is_simple_folder_creation(self, text: str) -> bool:
        """Check if input is a simple folder creation command that can be handled directly"""
        text_lower = text.lower()
        # Simple patterns that don't need AI interpretation
        simple_patterns = [
            r'^create\s+folder\s+(\w+)$',
            r'^make\s+folder\s+(\w+)$',
            r'^new\s+folder\s+(\w+)$',
            r'^create\s+directory\s+(\w+)$',
            r'^make\s+directory\s+(\w+)$',
            r'^new\s+directory\s+(\w+)$',
            r'^create\s+folder\s+called\s+(\w+)$',
            r'^make\s+folder\s+called\s+(\w+)$',
            r'^create\s+directory\s+called\s+(\w+)$',
            r'^make\s+directory\s+called\s+(\w+)$'
        ]
        return any(re.match(pattern, text_lower) for pattern in simple_patterns)
    
    def _is_simple_file_creation(self, text: str) -> bool:
        """Check if input is a simple file creation command that can be handled directly"""
        text_lower = text.lower()
        # Simple patterns that don't need AI interpretation
        simple_patterns = [
            r'^create\s+file\s+(\w+)$',
            r'^make\s+file\s+(\w+)$',
            r'^new\s+file\s+(\w+)$',
            r'^create\s+file\s+called\s+(\w+)$',
            r'^make\s+file\s+called\s+(\w+)$'
        ]
        return any(re.match(pattern, text_lower) for pattern in simple_patterns)
    
    def _is_system_query(self, text: str) -> bool:
        """Check if input is a system information query"""
        system_keywords = [
            'cpu', 'memory', 'disk', 'process', 'system', 'info',
            'usage', 'performance', 'status', 'running', 'active',
            'what time', 'current time', 'date', 'who am i', 'user',
            'files', 'directory', 'folder', 'list', 'show me',
            'what files', 'what is my', 'how much', 'how many'
        ]
        return any(keyword in text for keyword in system_keywords)
    
    def _is_chat_input(self, text: str) -> bool:
        """Check if input is conversational"""
        return any(keyword in text for keyword in self.chat_keywords)
    
    def _is_natural_language(self, text: str) -> bool:
        """Check if input is natural language command"""
        # Multi-word inputs that aren't direct commands
        words = text.split()
        if len(words) > 1:
            # Check if it contains action words or question words
            action_words = [
                'create', 'make', 'show', 'list', 'find', 'search',
                'move', 'copy', 'delete', 'remove', 'open', 'read',
                'write', 'save', 'edit', 'change', 'update', 'modify',
                'what', 'how', 'where', 'when', 'why', 'which', 'who'
            ]
            return any(word in text for word in action_words)
        return False
    
    def _handle_direct_command(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle direct terminal commands"""
        try:
            parts = user_input.split()
            cmd = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            # Execute the command
            output = run_command(cmd, args, session_id)
            
            # Update working directory if it changed
            if cmd == "cd" and not output.startswith("Error"):
                self.session_manager.update_working_directory(session_id, os.getcwd())
            
            return {
                "type": "direct_command",
                "result": output,
                "message": f"Executed: {user_input}",
                "command": cmd,
                "args": args
            }
        except Exception as e:
            return {
                "type": "error",
                "result": f"Error executing command: {str(e)}",
                "message": "Command execution failed"
            }
    
    def _handle_simple_folder_creation(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle simple folder creation commands directly (fast path)"""
        try:
            # Extract folder name using regex
            text_lower = user_input.lower()
            patterns = [
                r'^create\s+folder\s+(\w+)$',
                r'^make\s+folder\s+(\w+)$',
                r'^new\s+folder\s+(\w+)$',
                r'^create\s+directory\s+(\w+)$',
                r'^make\s+directory\s+(\w+)$',
                r'^new\s+directory\s+(\w+)$',
                r'^create\s+folder\s+called\s+(\w+)$',
                r'^make\s+folder\s+called\s+(\w+)$',
                r'^create\s+directory\s+called\s+(\w+)$',
                r'^make\s+directory\s+called\s+(\w+)$'
            ]
            
            folder_name = None
            for pattern in patterns:
                match = re.match(pattern, text_lower)
                if match:
                    folder_name = match.group(1)
                    break
            
            if not folder_name:
                return {
                    "type": "error",
                    "result": "Could not extract folder name",
                    "message": "Please specify a folder name"
                }
            
            # Execute mkdir command directly
            output = run_command("mkdir", [folder_name], session_id)
            
            return {
                "type": "simple_folder_creation",
                "result": output,
                "message": f"Created folder: {folder_name}",
                "folder_name": folder_name
            }
        except Exception as e:
            return {
                "type": "error",
                "result": f"Error creating folder: {str(e)}",
                "message": "Folder creation failed"
            }
    
    def _handle_simple_file_creation(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle simple file creation commands directly (fast path)"""
        try:
            # Extract file name using regex
            text_lower = user_input.lower()
            patterns = [
                r'^create\s+file\s+(\w+)$',
                r'^make\s+file\s+(\w+)$',
                r'^new\s+file\s+(\w+)$',
                r'^create\s+file\s+called\s+(\w+)$',
                r'^make\s+file\s+called\s+(\w+)$'
            ]
            
            file_name = None
            for pattern in patterns:
                match = re.match(pattern, text_lower)
                if match:
                    file_name = match.group(1)
                    break
            
            if not file_name:
                return {
                    "type": "error",
                    "result": "Could not extract file name",
                    "message": "Please specify a file name"
                }
            
            # Execute touch command directly
            output = run_command("touch", [file_name], session_id)
            
            return {
                "type": "simple_file_creation",
                "result": output,
                "message": f"Created file: {file_name}",
                "file_name": file_name
            }
        except Exception as e:
            return {
                "type": "error",
                "result": f"Error creating file: {str(e)}",
                "message": "File creation failed"
            }
    
    def _handle_file_operation(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle file operation requests"""
        try:
            # Use AI to interpret the file operation
            interpreted = self.ai_interpreter.interpret_command(user_input)
            
            if "command" in interpreted:
                command = interpreted["command"]
                parts = command.split()
                cmd = parts[0] if parts else ""
                args = parts[1:] if len(parts) > 1 else []
                
                # Execute the interpreted command
                output = run_command(cmd, args, session_id)
                
                return {
                    "type": "file_operation",
                    "result": output,
                    "message": f"File operation: {user_input} → {command}",
                    "interpreted_command": command
                }
            else:
                return {
                    "type": "error",
                    "result": "Could not interpret file operation",
                    "message": "Please try rephrasing your request"
                }
        except Exception as e:
            return {
                "type": "error",
                "result": f"Error processing file operation: {str(e)}",
                "message": "File operation failed"
            }
    
    def _handle_system_query(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle system information queries"""
        try:
            # Use AI to interpret the system query
            interpreted = self.ai_interpreter.interpret_command(user_input)
            
            if "command" in interpreted:
                command = interpreted["command"]
                parts = command.split()
                cmd = parts[0] if parts else ""
                args = parts[1:] if len(parts) > 1 else []
                
                # Execute the system command
                output = run_command(cmd, args, session_id)
                
                return {
                    "type": "system_query",
                    "result": output,
                    "message": f"System info: {user_input} → {command}",
                    "interpreted_command": command
                }
            else:
                return {
                    "type": "error",
                    "result": "Could not interpret system query",
                    "message": "Please try rephrasing your request"
                }
        except Exception as e:
            return {
                "type": "error",
                "result": f"Error processing system query: {str(e)}",
                "message": "System query failed"
            }
    
    def _handle_chat_input(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle conversational input"""
        try:
            # Add to chat context
            self.chat_context.append({"role": "user", "content": user_input})
            
            # Check if it's a request for help or information
            if any(word in user_input.lower() for word in ['help', 'how', 'what', 'explain', 'tell me']):
                return self._provide_help_response(user_input)
            
            # Check if it's a request for system information
            if any(word in user_input.lower() for word in ['cpu', 'memory', 'disk', 'process', 'system']):
                return self._handle_system_query(user_input, session_id)
            
            # Check if it's a request for file operations
            if any(word in user_input.lower() for word in ['create', 'make', 'file', 'folder', 'directory']):
                return self._handle_file_operation(user_input, session_id)
            
            # General conversational response
            response = self._generate_chat_response(user_input)
            
            # Add response to context
            self.chat_context.append({"role": "assistant", "content": response})
            
            return {
                "type": "chat",
                "result": response,
                "message": "Conversational response",
                "conversation_mode": True
            }
        except Exception as e:
            return {
                "type": "error",
                "result": f"Error in chat processing: {str(e)}",
                "message": "Chat processing failed"
            }
    
    def _handle_conversation_input(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle input when in conversation mode"""
        # In conversation mode, try to be more helpful and conversational
        # but still handle commands and requests
        
        # Check if it's a command disguised as conversation
        if any(word in user_input.lower() for word in ['run', 'execute', 'do', 'perform']):
            # Try to extract and execute commands
            return self._handle_natural_language(user_input, session_id)
        
        # Check if it's a request for help
        if any(word in user_input.lower() for word in ['help', 'how', 'what', 'explain', 'tell me']):
            return self._provide_help_response(user_input)
        
        # Check if it's a system query
        if any(word in user_input.lower() for word in ['cpu', 'memory', 'disk', 'process', 'system']):
            return self._handle_system_query(user_input, session_id)
        
        # Check if it's a file operation
        if any(word in user_input.lower() for word in ['create', 'make', 'file', 'folder', 'directory']):
            return self._handle_file_operation(user_input, session_id)
        
        # Otherwise, provide conversational response
        return self._handle_chat_input(user_input, session_id)
    
    def _handle_natural_language(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle natural language commands"""
        try:
            # Use AI to interpret the natural language
            interpreted = self.ai_interpreter.interpret_command(user_input)
            
            if "command" in interpreted:
                command = interpreted["command"]
                parts = command.split()
                cmd = parts[0] if parts else ""
                args = parts[1:] if len(parts) > 1 else []
                
                # Execute the interpreted command
                output = run_command(cmd, args, session_id)
                
                # Update working directory if it changed
                if cmd == "cd" and not output.startswith("Error"):
                    self.session_manager.update_working_directory(session_id, os.getcwd())
                
                return {
                    "type": "natural_language",
                    "result": output,
                    "message": f"Natural language: {user_input} → {command}",
                    "interpreted_command": command
                }
            else:
                return {
                    "type": "error",
                    "result": "Could not interpret natural language command",
                    "message": "Please try rephrasing your request"
                }
        except Exception as e:
            return {
                "type": "error",
                "result": f"Error processing natural language: {str(e)}",
                "message": "Natural language processing failed"
            }
    
    def _handle_unknown_input(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle unknown input types"""
        # Check if it might be a directory name or file
        if os.path.exists(user_input):
            if os.path.isdir(user_input):
                # It's a directory, offer to navigate to it
                return {
                    "type": "suggestion",
                    "result": f"'{user_input}' is a directory. Did you want to navigate to it?",
                    "message": "Try 'cd " + user_input + "' to navigate to this directory",
                    "suggestion": f"cd {user_input}"
                }
            else:
                # It's a file, offer to open it
                return {
                    "type": "suggestion", 
                    "result": f"'{user_input}' is a file. What would you like to do with it?",
                    "message": "Try 'cat " + user_input + "' to view it, or 'edit " + user_input + "' to edit it",
                    "suggestions": [f"cat {user_input}", f"edit {user_input}"]
                }
        
        # Check if it might be a partial command
        suggestions = self._get_command_suggestions(user_input)
        if suggestions:
            return {
                "type": "suggestion",
                "result": f"I'm not sure how to handle: '{user_input}'",
                "message": "Did you mean one of these commands?",
                "suggestions": suggestions
            }
        
        return {
            "type": "unknown",
            "result": f"I'm not sure how to handle: '{user_input}'",
            "message": "Try rephrasing or type 'help' for available commands"
        }
    
    def _get_command_suggestions(self, user_input: str) -> list:
        """Get command suggestions based on input"""
        user_input_lower = user_input.lower()
        suggestions = []
        
        # Common command suggestions
        if user_input_lower in ['ls', 'list']:
            suggestions.append('ls')
        elif user_input_lower in ['cd', 'change']:
            suggestions.append('cd <directory>')
        elif user_input_lower in ['mkdir', 'make']:
            suggestions.append('mkdir <directory>')
        elif user_input_lower in ['touch', 'create']:
            suggestions.append('touch <file>')
        elif user_input_lower in ['rm', 'delete']:
            suggestions.append('rm <file/folder>')
        elif user_input_lower in ['cp', 'copy']:
            suggestions.append('cp <source> <destination>')
        elif user_input_lower in ['mv', 'move']:
            suggestions.append('mv <source> <destination>')
        elif user_input_lower in ['cat', 'view']:
            suggestions.append('cat <file>')
        elif user_input_lower in ['edit', 'modify']:
            suggestions.append('edit <file>')
        elif user_input_lower in ['find', 'search']:
            suggestions.append('find <path> <pattern>')
        elif user_input_lower in ['grep', 'filter']:
            suggestions.append('grep <pattern> <file>')
        elif user_input_lower in ['ps', 'process']:
            suggestions.append('ps')
        elif user_input_lower in ['cpu', 'processor']:
            suggestions.append('cpu')
        elif user_input_lower in ['mem', 'memory']:
            suggestions.append('mem')
        elif user_input_lower in ['df', 'disk']:
            suggestions.append('df')
        elif user_input_lower in ['date', 'time']:
            suggestions.append('date')
        elif user_input_lower in ['whoami', 'user']:
            suggestions.append('whoami')
        elif user_input_lower in ['uname', 'system']:
            suggestions.append('uname')
        elif user_input_lower in ['clear', 'cls']:
            suggestions.append('clear')
        elif user_input_lower in ['history', 'commands']:
            suggestions.append('history')
        elif user_input_lower in ['help', '?']:
            suggestions.append('help')
        
        return suggestions
    
    def _provide_help_response(self, user_input: str) -> Dict[str, Any]:
        """Provide contextual help based on the input"""
        help_responses = {
            'help': "I can help you with commands, file operations, system info, and more! Try: 'ls', 'create a folder', 'what is my CPU usage?', or just chat with me!",
            'how': "I can show you how to do things! Try asking: 'how do I create a file?' or 'how do I check my system?'",
            'what': "I can tell you about your system, files, and help with commands! Try: 'what files do I have?' or 'what is my memory usage?'",
            'explain': "I can explain commands and concepts! Try: 'explain the ls command' or 'explain how to create folders'"
        }
        
        for keyword, response in help_responses.items():
            if keyword in user_input.lower():
                return {
                    "type": "help",
                    "result": response,
                    "message": "Help response"
                }
        
        return {
            "type": "help",
            "result": "I'm here to help! You can ask me about commands, file operations, system information, or just chat!",
            "message": "General help response"
        }
    
    def _generate_chat_response(self, user_input: str) -> str:
        """Generate a conversational response"""
        # Simple response generation based on context
        if 'hello' in user_input.lower() or 'hi' in user_input.lower():
            return "Hello! I'm your AI terminal assistant. I can help you with commands, file operations, system information, or just chat! What would you like to do?"
        
        elif 'thanks' in user_input.lower() or 'thank you' in user_input.lower():
            return "You're welcome! I'm here to help whenever you need me."
        
        elif 'bye' in user_input.lower() or 'goodbye' in user_input.lower():
            return "Goodbye! Feel free to come back anytime you need help!"
        
        elif 'name' in user_input.lower():
            return "I'm your AI terminal assistant! I can help you with all sorts of tasks. What's your name?"
        
        else:
            return "I understand! I'm here to help you with terminal commands, file operations, system information, or just to chat. What would you like to do next?"
    
    def get_conversation_context(self) -> list:
        """Get the current conversation context"""
        return self.chat_context
    
    def clear_conversation_context(self):
        """Clear the conversation context"""
        self.chat_context = []
    
    def is_conversation_mode(self) -> bool:
        """Check if we're in conversation mode"""
        return self.conversation_mode
