#!/usr/bin/env python3
"""
Python Terminal v3.0 - Smart AI-Assisted Multi-Session Terminal
"""

import os
import sys
from terminal import run_command
from session_manager import SessionManager
from history import load_history, save_history, add_command
from ai_interpreter import AICommandInterpreter
from enhanced_history import EnhancedHistoryManager
from chat_interface import ChatInterface
from command_parser import CommandParser
from help_system import HelpSystem
from unified_processor import UnifiedProcessor
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

def print_help():
    """Print available commands - now handled by HelpSystem"""
    help_system = HelpSystem()
    help_system.show_help()

def main():
    """Main CLI loop for Python Terminal v3.0 - Unified Mode"""
    # Initialize components
    console = Console()
    session_manager = SessionManager()
    history_manager = EnhancedHistoryManager()
    help_system = HelpSystem()
    
    # Check for OpenAI configuration
    use_openai = os.getenv('USE_OPENAI', 'false').lower() == 'true'
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    unified_processor = UnifiedProcessor(session_manager, use_openai=use_openai, openai_api_key=openai_api_key)

    # Create data directory if it doesn't exist
    os.makedirs("data/sessions", exist_ok=True)

    # Get current session
    current_session = session_manager.get_current_session()

    # Print welcome message
    welcome_text = Text("Python Terminal v3.0 - Unified Mode", style="bold blue")
    welcome_panel = Panel(
        "Smart AI-Assisted Multi-Session Terminal\n"
        "• Type anything: commands, natural language, or chat\n"
        "• Automatic detection and processing\n"
        "• Multi-session support with resource locking\n"
        "• Examples: 'ls', 'create a folder', 'hello', 'what is my CPU usage?'",
        title=welcome_text,
        border_style="blue"
    )
    console.print(welcome_panel)

    # Show current session info
    session_info = session_manager.get_session_details(current_session)
    if session_info:
        console.print(f"[cyan]Session: {current_session}[/cyan] | [dim]Commands: {session_info.get('command_count', 0)}[/dim] | [dim]Dir: {session_info.get('working_directory', os.getcwd())}[/dim]")
    else:
        console.print(f"[cyan]Session: {current_session}[/cyan]")
    
    # Show mode indicator
    mode_text = "Unified Mode - Type anything!" if not unified_processor.is_conversation_mode() else "Conversation Mode - Let's chat!"
    console.print(f"[green]{mode_text}[/green]")
    console.print()

    while True:
        try:
            # Prompt with session info and mode
            mode_indicator = "💬" if unified_processor.is_conversation_mode() else "⚡"
            prompt = f"[{current_session}] {mode_indicator} "
            user_input = input(prompt).strip()

            if not user_input:
                continue

            # Process input using unified processor
            result = unified_processor.process_input(user_input, current_session)
            
            # Handle special cases
            if result["type"] == "conversation_toggle":
                console.print(f"[bold cyan]{result['result']}[/bold cyan]")
                if result.get("conversation_mode"):
                    console.print("[dim]You can now chat naturally or use commands![/dim]")
                else:
                    console.print("[dim]Back to command mode. Type anything![/dim]")
                continue
            
            # Handle exit command
            if user_input.lower() in ['exit', 'quit', 'bye']:
                console.print("[bold green]Goodbye! 👋[/bold green]")
                # Clean up process session
                session_manager.cleanup_process_session()
                break
            
            # Handle help command
            if user_input.lower() == 'help':
                help_system.show_help()
                continue
            
            # Handle session management commands
            if user_input.lower() == 'newterm':
                new_session = session_manager.create_new_session()
                console.print(f"[green]Created new session: {new_session}[/green]")
                current_session = new_session
                continue
            elif user_input.lower() == 'sessions':
                sessions = session_manager.list_sessions()
                if sessions:
                    table = Table(title="Available Sessions", show_header=True, header_style="bold cyan")
                    table.add_column("Session ID", style="green")
                    table.add_column("Commands", style="yellow")
                    table.add_column("Working Directory", style="blue")
                    table.add_column("Status", style="magenta")
                    
                    for session in sessions:
                        details = session_manager.get_session_details(session)
                        if details:
                            status = "current" if session == current_session else "available"
                            table.add_row(
                                session,
                                str(details.get('command_count', 0)),
                                details.get('working_directory', 'N/A'),
                                status
                            )
                    console.print(table)
                else:
                    console.print("[yellow]No sessions found[/yellow]")
                continue
            elif user_input.lower().startswith('switch '):
                target_session = user_input.split(' ', 1)[1]
                if session_manager.switch_session(target_session):
                    console.print(f"[green]Switched to session: {target_session}[/green]")
                    current_session = target_session
                else:
                    console.print(f"[red]Session '{target_session}' not found[/red]")
                continue
            elif user_input.lower() == 'history':
                history = history_manager.get_session_history(current_session)
                if history:
                    console.print(f"[bold]Command history for {current_session}:[/bold]")
                    for i, cmd in enumerate(history[-20:], 1):  # Show last 20 commands
                        console.print(f"  {i:2d}: {cmd}")
                else:
                    console.print("[yellow]No command history[/yellow]")
                continue
            elif user_input.lower() == 'stats':
                stats = session_manager.get_session_stats()
                stats_table = Table(title="Session Statistics", show_header=True, header_style="bold cyan")
                stats_table.add_column("Metric", style="green")
                stats_table.add_column("Value", style="yellow")
                
                stats_table.add_row("Total Sessions", str(stats['total_sessions']))
                stats_table.add_row("Active Sessions", str(stats['active_sessions']))
                stats_table.add_row("Total Commands", str(stats['total_commands']))
                if stats['oldest_session']:
                    stats_table.add_row("Oldest Session", stats['oldest_session'])
                if stats['newest_session']:
                    stats_table.add_row("Newest Session", stats['newest_session'])
                
                console.print(stats_table)
                continue
            
            # Display result based on type
            if result["type"] == "error":
                console.print(f"[red]{result['result']}[/red]")
            elif result["type"] == "chat":
                console.print(f"[cyan]💬 {result['result']}[/cyan]")
            elif result["type"] in ["direct_command", "file_operation", "system_query", "natural_language", "simple_folder_creation", "simple_file_creation"]:
                if result.get("interpreted_command"):
                    console.print(f"[dim]→ {result['interpreted_command']}[/dim]")
                if result["result"]:
                    console.print(result["result"])
            elif result["type"] == "help":
                console.print(f"[green]💡 {result['result']}[/green]")
            elif result["type"] == "suggestion":
                console.print(f"[yellow]💡 {result['result']}[/yellow]")
                if result.get("message"):
                    console.print(f"[dim]{result['message']}[/dim]")
                if result.get("suggestion"):
                    console.print(f"[green]💡 Try: {result['suggestion']}[/green]")
                elif result.get("suggestions"):
                    console.print("[green]💡 Suggestions:[/green]")
                    for suggestion in result["suggestions"]:
                        console.print(f"  • {suggestion}")
            elif result["type"] == "unknown":
                console.print(f"[yellow]❓ {result['result']}[/yellow]")
            else:
                console.print(result["result"])
            
            # Save to history
            history_manager.add_command(current_session, user_input)
            
            # Update mode indicator if it changed
            if unified_processor.is_conversation_mode():
                mode_text = "Conversation Mode - Let's chat!"
            else:
                mode_text = "Unified Mode - Type anything!"

        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            continue
        except EOFError:
            console.print("\n[bold green]Goodbye! 👋[/bold green]")
            # Clean up process session
            session_manager.cleanup_process_session()
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

if __name__ == "__main__":
    main()
