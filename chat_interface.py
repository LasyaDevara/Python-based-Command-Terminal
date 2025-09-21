#!/usr/bin/env python3
"""
Chat-like interface for natural language terminal commands
"""

import os
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner
from ai_interpreter import AICommandInterpreter
from enhanced_history import EnhancedHistoryManager

class ChatInterface:
    def __init__(self, session_id: str = "default"):
        """
        Initialize the chat interface

        Args:
            session_id (str): The session ID for history tracking
        """
        self.console = Console()
        self.session_id = session_id
        self.ai_interpreter = AICommandInterpreter()
        self.history_manager = EnhancedHistoryManager()
        self.command_context = []  # Keep track of recent commands for context
        self.chat_mode = False

    def start_chat_mode(self):
        """Start the chat interface mode"""
        self.chat_mode = True
        self._print_welcome()

        try:
            while self.chat_mode:
                try:
                    # Get user input with rich prompt
                    user_input = self._get_user_input()

                    if not user_input:
                        continue

                    # Handle special commands
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        self._print_goodbye()
                        break
                    elif user_input.lower() == 'help':
                        self._show_chat_help()
                        continue
                    elif user_input.lower() == 'clear':
                        self.console.clear()
                        continue
                    elif user_input.lower() == 'history':
                        self._show_command_history()
                        continue

                    # Process the natural language command
                    self._process_chat_command(user_input)

                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Use 'exit' to quit chat mode[/yellow]")
                    continue
                except EOFError:
                    break

        except Exception as e:
            self.console.print(f"[red]Error in chat mode: {str(e)}[/red]")
        finally:
            self.chat_mode = False

    def _print_welcome(self):
        """Print welcome message for chat mode"""
        welcome_text = Text("🤖 AI Terminal Chat Mode", style="bold blue")
        welcome_panel = Panel(
            "You can now use natural language to execute terminal commands!\n"
            "Examples:\n"
            "• 'create a new folder called test'\n"
            "• 'show me running processes'\n"
            "• 'move file1.txt to the test folder'\n"
            "• 'list all files in current directory'\n\n"
            "Type 'help' for more options, 'exit' to quit.",
            title=welcome_text,
            border_style="blue"
        )
        self.console.print(welcome_panel)

    def _print_goodbye(self):
        """Print goodbye message"""
        goodbye_text = Text("👋 Goodbye!", style="bold green")
        self.console.print(goodbye_text)

    def _get_user_input(self) -> str:
        """Get user input with rich formatting"""
        return Prompt.ask(
            f"\n[bold cyan]Chat ({self.session_id})[/bold cyan]",
            default=""
        ).strip()

    def _show_chat_help(self):
        """Show help for chat mode"""
        help_table = Table(title="Chat Mode Commands")
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")

        help_table.add_row("help", "Show this help message")
        help_table.add_row("history", "Show command history")
        help_table.add_row("clear", "Clear the screen")
        help_table.add_row("exit/quit/bye", "Exit chat mode")
        help_table.add_row("Any natural language", "Execute as terminal command")

        self.console.print(help_table)

        # Show examples
        examples = Panel(
            "[bold]Natural Language Examples:[/bold]\n"
            "• 'create a new folder called test'\n"
            "• 'move file1.txt into the test folder'\n"
            "• 'show me the current directory'\n"
            "• 'list all running processes'\n"
            "• 'find all Python files in this directory'",
            title="Examples",
            border_style="green"
        )
        self.console.print(examples)

    def _show_command_history(self):
        """Show command history in chat mode"""
        history = self.history_manager.get_session_history(self.session_id)

        if not history:
            self.console.print("[yellow]No command history yet.[/yellow]")
            return

        history_table = Table(title="Command History")
        history_table.add_column("Time", style="cyan", no_wrap=True)
        history_table.add_column("Command", style="white")

        for i, cmd in enumerate(history[-10:], 1):  # Show last 10 commands
            history_table.add_row(str(i), cmd)

        self.console.print(history_table)

    def _process_chat_command(self, user_input: str):
        """Process a natural language command"""
        try:
            # Show processing indicator
            with self.console.status("[bold green]Processing command...", spinner="dots") as status:
                # Interpret the natural language command
                result = self.ai_interpreter.interpret_command(user_input)

            # Display the interpreted command
            if "command" in result:
                command = result["command"]
                self._display_interpreted_command(user_input, command)

                # Ask for confirmation
                if self._confirm_execution(command):
                    # Execute the command
                    self._execute_command(command)
                else:
                    self.console.print("[yellow]Command cancelled.[/yellow]")

            elif "commands" in result:
                commands = result["commands"]
                self._display_interpreted_commands(user_input, commands)

                # Ask for confirmation
                if self._confirm_execution_multiple(commands):
                    # Execute all commands
                    for cmd in commands:
                        self._execute_command(cmd)
                else:
                    self.console.print("[yellow]Commands cancelled.[/yellow]")

            else:
                self.console.print("[red]Could not interpret command. Please try rephrasing.[/red]")

        except Exception as e:
            self.console.print(f"[red]Error processing command: {str(e)}[/red]")

    def _display_interpreted_command(self, original: str, command: str):
        """Display the interpreted command"""
        table = Table(show_header=False, show_edge=False, pad_edge=False)
        table.add_column("Type", style="cyan", width=12)
        table.add_column("Content", style="white")

        table.add_row("Original:", original)
        table.add_row("Command:", command)

        self.console.print(Panel(
            table,
            title="Command Interpretation",
            border_style="green"
        ))

    def _display_interpreted_commands(self, original: str, commands: List[str]):
        """Display multiple interpreted commands"""
        table = Table(show_header=False, show_edge=False, pad_edge=False)
        table.add_column("Type", style="cyan", width=12)
        table.add_column("Content", style="white")

        table.add_row("Original:", original)
        for i, cmd in enumerate(commands, 1):
            table.add_row(f"Command {i}:", cmd)

        self.console.print(Panel(
            table,
            title="Command Interpretation",
            border_style="green"
        ))

    def _confirm_execution(self, command: str) -> bool:
        """Auto-confirm command execution (ChatGPT style)"""
        return True  # Auto-execute like ChatGPT

    def _confirm_execution_multiple(self, commands: List[str]) -> bool:
        """Auto-confirm multiple command execution (ChatGPT style)"""
        return True  # Auto-execute like ChatGPT

    def _execute_command(self, command: str):
        """Execute a command and show result"""
        try:
            # Import here to avoid circular imports
            from terminal import run_command

            # Parse command and arguments
            parts = command.split()
            cmd = parts[0] if parts else ""
            args = parts[1:] if len(parts) > 1 else []

            # Execute the command
            with self.console.status(f"[bold green]Executing: {command}...[/bold green]", spinner="dots"):
                output = run_command(cmd, args)

            # Display result
            if output:
                result_panel = Panel(
                    output,
                    title=f"Result: {command}",
                    border_style="blue"
                )
                self.console.print(result_panel)
            else:
                self.console.print(f"[green]✓ Command executed successfully: {command}[/green]")

            # Add to history
            self.history_manager.add_command(self.session_id, command)

        except Exception as e:
            error_panel = Panel(
                str(e),
                title=f"Error executing: {command}",
                border_style="red"
            )
            self.console.print(error_panel)

    def process_single_command(self, user_input: str) -> Optional[str]:
        """
        Process a single natural language command and return the interpreted command

        Args:
            user_input (str): The natural language input

        Returns:
            str: The interpreted command, or None if not interpretable
        """
        try:
            result = self.ai_interpreter.interpret_command(user_input)

            if "command" in result:
                return result["command"]
            elif "commands" in result:
                # Return the first command if multiple
                return result["commands"][0]

        except Exception:
            pass

        return None
