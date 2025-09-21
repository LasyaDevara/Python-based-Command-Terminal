#!/usr/bin/env python3
"""
Comprehensive help system for the AI terminal
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns

class HelpSystem:
    def __init__(self):
        """Initialize the help system"""
        self.console = Console()
        
        # Command categories
        self.commands = {
            "Session Management": {
                "newterm": "Start a new terminal session",
                "sessions": "List all existing sessions",
                "switch <id>": "Switch to another session",
                "history": "Show command history for current session"
            },
            "File Operations": {
                "pwd": "Print current working directory",
                "ls [path]": "List directory contents",
                "cd <dir>": "Change directory",
                "mkdir <dir>": "Create directory",
                "touch <file>": "Create empty file",
                "rm <file/folder>": "Remove file or directory",
                "cp <src> <dest>": "Copy file or directory",
                "mv <src> <dest>": "Move/rename file or directory",
                "cat <file>": "Display file contents",
                "edit <file>": "Edit file content",
                "find <path> <pattern>": "Find files by name pattern",
                "grep <pattern> <file>": "Search for pattern in file"
            },
            "System Information": {
                "ps": "Show running processes",
                "cpu": "Show CPU usage",
                "mem": "Show memory usage",
                "df": "Show disk usage",
                "date": "Show current date and time",
                "whoami": "Show current user",
                "uname": "Show system information"
            },
            "AI & Chat": {
                "chat": "Enter AI chat mode for natural language commands",
                "ai <query>": "Use AI to interpret natural language command",
                "help": "Show this help message",
                "clear": "Clear the terminal screen",
                "echo <text>": "Print text to terminal"
            },
            "Control": {
                "exit": "Exit current session",
                "help <command>": "Get detailed help for a specific command"
            }
        }
        
        # Natural language examples
        self.natural_language_examples = [
            "create a new folder called test",
            "create a new file called main.py",
            "move file1.txt to the test folder",
            "copy config.txt to backup.txt",
            "show me the current directory",
            "list all files in current folder",
            "list folders",
            "show running processes",
            "what is the CPU usage?",
            "show memory usage",
            "how many files in current folder?",
            "find all Python files",
            "search for 'hello' in main.py",
            "edit the file config.txt",
            "show me the contents of readme.txt",
            "what time is it?",
            "who am I?",
            "what system am I running?",
            "how much disk space do I have?",
            "remove folder test1",
            "delete file test.txt"
        ]

    def show_help(self, command: str = None):
        """
        Show help information
        
        Args:
            command (str, optional): Specific command to get help for
        """
        if command:
            self._show_command_help(command)
        else:
            self._show_main_help()

    def _show_main_help(self):
        """Show the main help screen"""
        # Welcome message
        welcome_text = Text("Python Terminal v3.0 - AI-Assisted Multi-Session Terminal", style="bold blue")
        welcome_panel = Panel(
            "Welcome to the smart AI-assisted terminal! You can use both traditional commands and natural language.\n"
            "Type 'help <command>' for detailed information about a specific command.",
            title=welcome_text,
            border_style="blue"
        )
        self.console.print(welcome_panel)
        self.console.print()

        # Show command categories
        for category, commands in self.commands.items():
            self._show_command_category(category, commands)
            self.console.print()

        # Show natural language examples
        self._show_natural_language_examples()

    def _show_command_category(self, category: str, commands: dict):
        """Show a category of commands"""
        table = Table(title=category, show_header=True, header_style="bold cyan")
        table.add_column("Command", style="green", no_wrap=True)
        table.add_column("Description", style="white")

        for cmd, desc in commands.items():
            table.add_row(cmd, desc)

        self.console.print(table)

    def _show_natural_language_examples(self):
        """Show natural language examples"""
        examples_text = Text("Natural Language Examples", style="bold magenta")
        examples_panel = Panel(
            "You can use natural language for many operations:\n\n" +
            "\n".join(f"• {example}" for example in self.natural_language_examples[:10]) +
            "\n\n... and many more! The AI will interpret your intent and execute the appropriate commands.",
            title=examples_text,
            border_style="magenta"
        )
        self.console.print(examples_panel)

    def _show_command_help(self, command: str):
        """Show detailed help for a specific command"""
        command = command.lower()
        
        # Find the command in our categories
        found = False
        for category, commands in self.commands.items():
            if command in commands:
                self.console.print(f"[bold cyan]Help for '{command}':[/bold cyan]")
                self.console.print(f"[green]{command}[/green] - {commands[command]}")
                
                # Add usage examples
                examples = self._get_command_examples(command)
                if examples:
                    self.console.print("\n[bold]Examples:[/bold]")
                    for example in examples:
                        self.console.print(f"  [dim]{example}[/dim]")
                
                found = True
                break
        
        if not found:
            self.console.print(f"[red]Command '{command}' not found. Type 'help' to see all available commands.[/red]")

    def _get_command_examples(self, command: str) -> list:
        """Get usage examples for a command"""
        examples = {
            "mkdir": ["mkdir test", "mkdir projects/myapp", "mkdir -p path/to/dir"],
            "touch": ["touch file.txt", "touch newfile.py", "touch config.json"],
            "rm": ["rm file.txt", "rm -rf folder", "rm *.tmp"],
            "cp": ["cp file.txt backup.txt", "cp -r folder backup_folder", "cp *.py /backup/"],
            "mv": ["mv old.txt new.txt", "mv file.txt folder/", "mv *.log /logs/"],
            "cat": ["cat file.txt", "cat config.json", "cat README.md"],
            "edit": ["edit config.txt", "edit main.py", "edit README.md"],
            "find": ["find . -name '*.py'", "find /home -name 'config'", "find . -type f -name '*.txt'"],
            "grep": ["grep 'error' log.txt", "grep -r 'function' src/", "grep -i 'warning' *.log"],
            "ls": ["ls", "ls -la", "ls /home", "ls *.py"],
            "cd": ["cd /home", "cd ..", "cd projects/myapp"],
            "ps": ["ps", "ps aux", "ps -ef"],
            "chat": ["chat", "Enter chat mode and type natural language commands"],
            "ai": ["ai 'create a new folder called test'", "ai 'show me running processes'", "ai 'what is the CPU usage?'"]
        }
        
        return examples.get(command, [])

    def show_quick_reference(self):
        """Show a quick reference card"""
        quick_ref = Panel(
            "[bold]Quick Reference:[/bold]\n\n"
            "[green]Session:[/green] newterm, sessions, switch <id>, history\n"
            "[green]Files:[/green] ls, cd, mkdir, touch, rm, cp, mv, cat, edit\n"
            "[green]System:[/green] ps, cpu, mem, df, date, whoami, uname\n"
            "[green]AI:[/green] chat, ai <query>\n"
            "[green]Control:[/green] help, clear, exit\n\n"
            "[bold]Natural Language:[/bold] Just type what you want to do!",
            title="Quick Reference",
            border_style="yellow"
        )
        self.console.print(quick_ref)

    def show_feature_highlights(self):
        """Show feature highlights"""
        features = [
            "🤖 AI-Powered: Use natural language for commands",
            "🔄 Multi-Session: Run multiple terminal sessions simultaneously",
            "🔒 Resource Locking: Prevents conflicts between sessions",
            "📁 File Operations: Complete file and directory management",
            "💾 Persistent History: Command history saved per session",
            "🎯 Smart Parsing: Automatically detects command vs natural language",
            "🖥️ Windows Compatible: Works on Windows, Linux, and macOS",
            "📊 System Info: Built-in system monitoring commands"
        ]
        
        features_text = "\n".join(features)
        features_panel = Panel(
            features_text,
            title="🚀 Feature Highlights",
            border_style="green"
        )
        self.console.print(features_panel)

    def show_troubleshooting(self):
        """Show troubleshooting information"""
        troubleshooting = Panel(
            "[bold]Common Issues & Solutions:[/bold]\n\n"
            "[yellow]Q: AI commands not working?[/yellow]\n"
            "A: Make sure Ollama is installed and running. Try 'ollama list' to check.\n\n"
            "[yellow]Q: Resource locked by another session?[/yellow]\n"
            "A: Wait a few minutes or check which session is using the resource.\n\n"
            "[yellow]Q: Command not found?[/yellow]\n"
            "A: Try using natural language or check 'help' for available commands.\n\n"
            "[yellow]Q: Session not switching?[/yellow]\n"
            "A: Use 'sessions' to see available sessions, then 'switch <id>'.\n\n"
            "[yellow]Q: File operations failing?[/yellow]\n"
            "A: Check file permissions and make sure the path exists.",
            title="🔧 Troubleshooting",
            border_style="red"
        )
        self.console.print(troubleshooting)

