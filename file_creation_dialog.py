#!/usr/bin/env python3
"""
File and folder creation dialog with path selection
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text

class FileCreationDialog:
    def __init__(self):
        """Initialize the file creation dialog"""
        self.console = Console()
    
    def select_file_or_folder(self, title="Select File or Folder", allow_files=True, allow_folders=True):
        """
        Open file/folder selection dialog
        
        Args:
            title (str): Dialog title
            allow_files (bool): Allow file selection
            allow_folders (bool): Allow folder selection
            
        Returns:
            tuple: (success, path, message)
        """
        try:
            if self._has_gui():
                return self._select_file_or_folder_gui(title, allow_files, allow_folders)
            else:
                return self._select_file_or_folder_cli(title, allow_files, allow_folders)
        except Exception as e:
            return False, None, f"Error selecting file/folder: {str(e)}"
    
    def select_destination(self, source_path, operation="move"):
        """
        Select destination for file/folder operations
        
        Args:
            source_path (str): Source file/folder path
            operation (str): Operation type (move, copy, etc.)
            
        Returns:
            tuple: (success, destination_path, message)
        """
        try:
            if self._has_gui():
                return self._select_destination_gui(source_path, operation)
            else:
                return self._select_destination_cli(source_path, operation)
        except Exception as e:
            return False, None, f"Error selecting destination: {str(e)}"
    
    def create_file_with_path(self, filename=None, session_id="default"):
        """
        Create a file with path selection dialog
        
        Args:
            filename (str, optional): Suggested filename
            session_id (str): Current session ID
            
        Returns:
            tuple: (success, filepath, message)
        """
        try:
            # Try to use GUI dialog first
            if self._has_gui():
                return self._create_file_gui(filename)
            else:
                return self._create_file_cli(filename, session_id)
        except Exception as e:
            return False, None, f"Error creating file: {str(e)}"
    
    def create_folder_with_path(self, foldername=None, session_id="default"):
        """
        Create a folder with path selection dialog
        
        Args:
            foldername (str, optional): Suggested folder name
            session_id (str): Current session ID
            
        Returns:
            tuple: (success, folderpath, message)
        """
        try:
            # Try to use GUI dialog first
            if self._has_gui():
                return self._create_folder_gui(foldername)
            else:
                return self._create_folder_cli(foldername, session_id)
        except Exception as e:
            return False, None, f"Error creating folder: {str(e)}"
    
    def _has_gui(self):
        """Check if GUI is available"""
        try:
            import tkinter
            return True
        except ImportError:
            return False
    
    def _select_file_or_folder_gui(self, title, allow_files=True, allow_folders=True):
        """Select file or folder using GUI dialog"""
        try:
            root = tk.Tk()
            root.withdraw()
            
            if allow_files and allow_folders:
                # Show both files and folders
                filepath = filedialog.askopenfilename(
                    title=title,
                    filetypes=[
                        ("All files", "*.*"),
                        ("Text files", "*.txt"),
                        ("Python files", "*.py"),
                        ("Directories", "*/")
                    ]
                )
            elif allow_files:
                filepath = filedialog.askopenfilename(title=title)
            else:
                filepath = filedialog.askdirectory(title=title)
            
            root.destroy()
            
            if not filepath:
                return False, None, "Selection cancelled"
            
            return True, filepath, f"Selected: {filepath}"
            
        except Exception as e:
            return False, None, f"GUI error: {str(e)}"
    
    def _select_file_or_folder_cli(self, title, allow_files=True, allow_folders=True):
        """Select file or folder using CLI interface"""
        try:
            current_dir = os.getcwd()
            self.console.print(f"[cyan]{title}[/cyan]")
            self.console.print(f"[dim]Current directory: {current_dir}[/dim]")
            
            while True:
                try:
                    items = os.listdir(current_dir)
                    files = [item for item in items if os.path.isfile(os.path.join(current_dir, item))]
                    dirs = [item for item in items if os.path.isdir(os.path.join(current_dir, item))]
                    
                    files.sort()
                    dirs.sort()
                    
                    # Show items
                    self.console.print(f"\n[bold]Contents of {current_dir}:[/bold]")
                    
                    if allow_folders and dirs:
                        self.console.print("[green]Directories:[/green]")
                        for i, dir_name in enumerate(dirs, 1):
                            self.console.print(f"  {i:2d}. [blue]{dir_name}/[/blue]")
                    
                    if allow_files and files:
                        self.console.print("[green]Files:[/green]")
                        for i, file_name in enumerate(files, len(dirs) + 1):
                            self.console.print(f"  {i:2d}. {file_name}")
                    
                    self.console.print("  0. Select current directory")
                    self.console.print("  b. Go back")
                    self.console.print("  q. Quit")
                    
                    choice = Prompt.ask("Select option", default="q")
                    
                    if choice == "q":
                        return False, None, "Selection cancelled"
                    elif choice == "b":
                        parent = os.path.dirname(current_dir)
                        if parent != current_dir:
                            current_dir = parent
                        else:
                            self.console.print("[yellow]Already at root directory[/yellow]")
                    elif choice == "0":
                        return True, current_dir, f"Selected directory: {current_dir}"
                    else:
                        try:
                            item_index = int(choice) - 1
                            if 0 <= item_index < len(dirs):
                                # Selected a directory
                                if allow_folders:
                                    selected_path = os.path.join(current_dir, dirs[item_index])
                                    return True, selected_path, f"Selected directory: {selected_path}"
                                else:
                                    current_dir = os.path.join(current_dir, dirs[item_index])
                            elif len(dirs) <= item_index < len(dirs) + len(files):
                                # Selected a file
                                if allow_files:
                                    file_index = item_index - len(dirs)
                                    selected_path = os.path.join(current_dir, files[file_index])
                                    return True, selected_path, f"Selected file: {selected_path}"
                                else:
                                    self.console.print("[red]Files not allowed in this selection[/red]")
                            else:
                                self.console.print("[red]Invalid selection[/red]")
                        except ValueError:
                            self.console.print("[red]Invalid selection[/red]")
                
                except PermissionError:
                    self.console.print("[red]Permission denied to access directory[/red]")
                    break
                except Exception as e:
                    self.console.print(f"[red]Error browsing directory: {e}[/red]")
                    break
            
            return False, None, "Selection cancelled"
            
        except Exception as e:
            return False, None, f"CLI error: {str(e)}"
    
    def _select_destination_gui(self, source_path, operation):
        """Select destination using GUI dialog"""
        try:
            root = tk.Tk()
            root.withdraw()
            
            # Ask for destination directory
            dest_dir = filedialog.askdirectory(
                title=f"Select destination for {operation} operation"
            )
            
            if not dest_dir:
                root.destroy()
                return False, None, f"{operation.capitalize()} cancelled"
            
            # Get source name
            source_name = os.path.basename(source_path)
            dest_path = os.path.join(dest_dir, source_name)
            
            root.destroy()
            return True, dest_path, f"Destination: {dest_path}"
            
        except Exception as e:
            return False, None, f"GUI error: {str(e)}"
    
    def _select_destination_cli(self, source_path, operation):
        """Select destination using CLI interface"""
        try:
            source_name = os.path.basename(source_path)
            self.console.print(f"[cyan]{operation.capitalize()} '{source_name}' to:[/cyan]")
            
            current_dir = os.getcwd()
            self.console.print(f"[dim]Current directory: {current_dir}[/dim]")
            
            # Use the same directory browser as file selection
            dest_path = self._browse_directory_cli(source_name, "destination")
            
            if not dest_path:
                return False, None, f"{operation.capitalize()} cancelled"
            
            return True, dest_path, f"Destination: {dest_path}"
            
        except Exception as e:
            return False, None, f"CLI error: {str(e)}"
    
    def _create_file_gui(self, filename=None):
        """Create file using GUI dialog"""
        try:
            # Create a hidden root window
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Set initial filename
            if filename:
                initialfile = filename
            else:
                initialfile = "new_file.txt"
            
            # Ask for save location
            filepath = filedialog.asksaveasfilename(
                title="Create New File",
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("Python files", "*.py"),
                    ("All files", "*.*")
                ],
                initialfile=initialfile
            )
            
            root.destroy()
            
            if not filepath:
                return False, None, "File creation cancelled"
            
            # Create the file
            Path(filepath).touch()
            return True, filepath, f"File created: {filepath}"
            
        except Exception as e:
            return False, None, f"GUI error: {str(e)}"
    
    def _create_folder_gui(self, foldername=None):
        """Create folder using GUI dialog"""
        try:
            # Create a hidden root window
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Ask for folder location
            folderpath = filedialog.askdirectory(
                title="Select Location for New Folder"
            )
            
            if not folderpath:
                root.destroy()
                return False, None, "Folder creation cancelled"
            
            # Set folder name
            if foldername:
                folder_name = foldername
            else:
                folder_name = "new_folder"
            
            # Create full path
            full_path = os.path.join(folderpath, folder_name)
            
            # Check if folder already exists
            if os.path.exists(full_path):
                root.destroy()
                return False, None, f"Folder already exists: {full_path}"
            
            # Create the folder
            os.makedirs(full_path, exist_ok=True)
            root.destroy()
            
            return True, full_path, f"Folder created: {full_path}"
            
        except Exception as e:
            return False, None, f"GUI error: {str(e)}"
    
    def _create_file_cli(self, filename=None, session_id="default"):
        """Create file using CLI interface"""
        try:
            # Show current directory
            current_dir = os.getcwd()
            self.console.print(f"[cyan]Current directory: {current_dir}[/cyan]")
            
            # Ask for filename
            if not filename:
                filename = Prompt.ask("Enter filename", default="new_file.txt")
            
            # Ask for path
            path_choice = Prompt.ask(
                "Where would you like to create the file?",
                choices=["current", "browse", "custom"],
                default="current"
            )
            
            if path_choice == "current":
                filepath = os.path.join(current_dir, filename)
            elif path_choice == "browse":
                # Show directory browser
                filepath = self._browse_directory_cli(filename, "file")
                if not filepath:
                    return False, None, "File creation cancelled"
            else:  # custom
                custom_path = Prompt.ask("Enter full path (including filename)")
                filepath = custom_path
            
            # Create the file
            Path(filepath).touch()
            return True, filepath, f"File created: {filepath}"
            
        except Exception as e:
            return False, None, f"CLI error: {str(e)}"
    
    def _create_folder_cli(self, foldername=None, session_id="default"):
        """Create folder using CLI interface"""
        try:
            # Show current directory
            current_dir = os.getcwd()
            self.console.print(f"[cyan]Current directory: {current_dir}[/cyan]")
            
            # Ask for folder name
            if not foldername:
                foldername = Prompt.ask("Enter folder name", default="new_folder")
            
            # Ask for path
            path_choice = Prompt.ask(
                "Where would you like to create the folder?",
                choices=["current", "browse", "custom"],
                default="current"
            )
            
            if path_choice == "current":
                folderpath = os.path.join(current_dir, foldername)
            elif path_choice == "browse":
                # Show directory browser
                folderpath = self._browse_directory_cli(foldername, "folder")
                if not folderpath:
                    return False, None, "Folder creation cancelled"
            else:  # custom
                custom_path = Prompt.ask("Enter full path (including folder name)")
                folderpath = custom_path
            
            # Create the folder
            os.makedirs(folderpath, exist_ok=True)
            return True, folderpath, f"Folder created: {folderpath}"
            
        except Exception as e:
            return False, None, f"CLI error: {str(e)}"
    
    def _browse_directory_cli(self, name, item_type):
        """Browse directories using CLI"""
        try:
            current_dir = os.getcwd()
            self.console.print(f"[cyan]Browsing directories from: {current_dir}[/cyan]")
            
            while True:
                # Show current directory contents
                try:
                    items = os.listdir(current_dir)
                    dirs = [item for item in items if os.path.isdir(os.path.join(current_dir, item))]
                    dirs.sort()
                    
                    if not dirs:
                        self.console.print("[yellow]No subdirectories found[/yellow]")
                        break
                    
                    # Show directory options
                    self.console.print(f"\n[bold]Directories in {current_dir}:[/bold]")
                    for i, dir_name in enumerate(dirs, 1):
                        self.console.print(f"  {i:2d}. {dir_name}")
                    
                    self.console.print(f"  0. Create {item_type} here")
                    self.console.print("  b. Go back")
                    self.console.print("  q. Quit")
                    
                    choice = Prompt.ask("Select option", default="0")
                    
                    if choice == "q":
                        return None
                    elif choice == "b":
                        # Go back to parent directory
                        parent = os.path.dirname(current_dir)
                        if parent != current_dir:
                            current_dir = parent
                        else:
                            self.console.print("[yellow]Already at root directory[/yellow]")
                    elif choice == "0":
                        # Create item here
                        if item_type == "file":
                            return os.path.join(current_dir, name)
                        else:
                            return os.path.join(current_dir, name)
                    else:
                        try:
                            # Navigate to selected directory
                            dir_index = int(choice) - 1
                            if 0 <= dir_index < len(dirs):
                                current_dir = os.path.join(current_dir, dirs[dir_index])
                            else:
                                self.console.print("[red]Invalid selection[/red]")
                        except ValueError:
                            self.console.print("[red]Invalid selection[/red]")
                
                except PermissionError:
                    self.console.print("[red]Permission denied to access directory[/red]")
                    break
                except Exception as e:
                    self.console.print(f"[red]Error browsing directory: {e}[/red]")
                    break
            
            return None
            
        except Exception as e:
            self.console.print(f"[red]Error in directory browser: {e}[/red]")
            return None
    
    def show_path_help(self):
        """Show help for path selection"""
        help_text = """
[bold]Path Selection Options:[/bold]

[green]GUI Mode (if available):[/green]
• A file/folder dialog will open
• Navigate to your desired location
• Enter the name for your file/folder
• Click Save/OK to create

[green]CLI Mode:[/green]
• [cyan]current[/cyan] - Create in current directory
• [cyan]browse[/cyan] - Browse directories to select location
• [cyan]custom[/cyan] - Enter full path manually

[green]Directory Browser:[/green]
• Use numbers to select directories
• Use 'b' to go back to parent directory
• Use '0' to create item in current location
• Use 'q' to quit without creating
        """
        
        self.console.print(Panel(help_text, title="Path Selection Help", border_style="blue"))
