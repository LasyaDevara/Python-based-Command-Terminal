#!/usr/bin/env python3
"""
Command execution logic for the terminal with Windows support and resource locking
"""

import os
import shutil
import psutil
import subprocess
import time
import threading
import json
from pathlib import Path

# Global resource locks to prevent conflicts between sessions
_resource_locks = {}
_lock_file = "data/resource_locks.json"

def _load_locks():
    """Load resource locks from file"""
    try:
        if os.path.exists(_lock_file):
            with open(_lock_file, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {}

def _save_locks(locks):
    """Save resource locks to file"""
    try:
        os.makedirs(os.path.dirname(_lock_file), exist_ok=True)
        with open(_lock_file, 'w') as f:
            json.dump(locks, f)
    except IOError:
        pass

def _acquire_lock(session_id, resource_path):
    """Acquire a lock on a resource"""
    locks = _load_locks()
    current_time = time.time()
    
    # Clean up expired locks (older than 5 minutes)
    for resource, lock_info in list(locks.items()):
        if current_time - lock_info.get('timestamp', 0) > 300:  # 5 minutes
            del locks[resource]
    
    # Check if resource is already locked by another session
    if resource_path in locks and locks[resource_path]['session_id'] != session_id:
        return False
    
    # Acquire the lock
    locks[resource_path] = {
        'session_id': session_id,
        'timestamp': current_time
    }
    _save_locks(locks)
    return True

def _release_lock(session_id, resource_path):
    """Release a lock on a resource"""
    locks = _load_locks()
    if resource_path in locks and locks[resource_path]['session_id'] == session_id:
        del locks[resource_path]
        _save_locks(locks)

def _check_lock(session_id, resource_path):
    """Check if a resource is locked by another session"""
    locks = _load_locks()
    if resource_path in locks and locks[resource_path]['session_id'] != session_id:
        return locks[resource_path]['session_id']
    return None

def run_command(cmd, args, session_id="default"):
    """
    Execute a command and return its output as a string

    Args:
        cmd (str): The command to execute
        args (list): Arguments for the command
        session_id (str): The session ID for resource locking

    Returns:
        str: Output of the command or error message
    """
    try:
        if cmd == "pwd":
            return os.getcwd()

        elif cmd == "ls":
            # List directory contents
            path = args[0] if args else "."
            try:
                items = os.listdir(path)
                return "\n".join(items)
            except OSError as e:
                return f"Error: {str(e)}"

        elif cmd == "cd":
            if not args:
                return "Usage: cd <directory>"
            try:
                os.chdir(args[0])
                return ""
            except OSError as e:
                return f"Error: {str(e)}"

        elif cmd == "mkdir":
            if not args:
                # Use file creation dialog for interactive folder creation
                from file_creation_dialog import FileCreationDialog
                dialog = FileCreationDialog()
                success, folderpath, message = dialog.create_folder_with_path(session_id=session_id)
                if success:
                    return message
                else:
                    return message
            else:
                target = args[0]
                try:
                    # Check for lock
                    locked_by = _check_lock(session_id, os.path.abspath(target))
                    if locked_by:
                        return f"Resource is being used by another session. Wait."
                    
                    # Acquire lock
                    if not _acquire_lock(session_id, os.path.abspath(target)):
                        return f"Resource is being used by another session. Wait."
                    
                    os.makedirs(target, exist_ok=True)
                    _release_lock(session_id, os.path.abspath(target))
                    return f"Directory '{target}' created"
                except OSError as e:
                    _release_lock(session_id, os.path.abspath(target))
                    return f"Error: {str(e)}"

        elif cmd == "touch":
            if not args:
                # Use file creation dialog for interactive file creation
                from file_creation_dialog import FileCreationDialog
                dialog = FileCreationDialog()
                success, filepath, message = dialog.create_file_with_path(session_id=session_id)
                if success:
                    return message
                else:
                    return message
            else:
                target = args[0]
                try:
                    # Check for lock
                    locked_by = _check_lock(session_id, os.path.abspath(target))
                    if locked_by:
                        return f"Resource is being used by another session. Wait."
                    
                    # Acquire lock
                    if not _acquire_lock(session_id, os.path.abspath(target)):
                        return f"Resource is being used by another session. Wait."
                    
                    Path(target).touch()
                    _release_lock(session_id, os.path.abspath(target))
                    return f"File '{target}' created"
                except OSError as e:
                    _release_lock(session_id, os.path.abspath(target))
                    return f"Error: {str(e)}"

        elif cmd == "rm":
            if not args:
                return "Error: missing file/folder"
            target = args[0]
            if not os.path.exists(target):
                return f"Error: {target} does not exist"
            
            try:
                # Check for lock
                locked_by = _check_lock(session_id, os.path.abspath(target))
                if locked_by:
                    return f"Resource is being used by another session. Wait."
                
                # Acquire lock
                if not _acquire_lock(session_id, os.path.abspath(target)):
                    return f"Resource is being used by another session. Wait."
                
                if os.path.isdir(target):
                    shutil.rmtree(target)
                    result = f"Directory '{target}' removed"
                else:
                    os.remove(target)
                    result = f"File '{target}' removed"
                
                _release_lock(session_id, os.path.abspath(target))
                return result
            except OSError as e:
                _release_lock(session_id, os.path.abspath(target))
                return f"Error: {str(e)}"

        elif cmd == "cp":
            if len(args) < 2:
                # Use file dialog to select source and destination
                from file_creation_dialog import FileCreationDialog
                dialog = FileCreationDialog()
                
                # Select source
                success, source, message = dialog.select_file_or_folder("Select file/folder to copy", allow_files=True, allow_folders=True)
                if not success:
                    return message
                
                # Select destination
                success, dest, message = dialog.select_destination(source, "copy")
                if not success:
                    return message
            else:
                source, dest = args[0], args[1]
            
            if not os.path.exists(source):
                return f"Error: {source} does not exist"
            
            try:
                # Check for locks on both source and destination
                locked_by = _check_lock(session_id, os.path.abspath(source))
                if locked_by:
                    return f"Source resource is being used by another session. Wait."
                
                locked_by = _check_lock(session_id, os.path.abspath(dest))
                if locked_by:
                    return f"Destination resource is being used by another session. Wait."
                
                # Acquire locks
                if not _acquire_lock(session_id, os.path.abspath(source)):
                    return f"Source resource is being used by another session. Wait."
                if not _acquire_lock(session_id, os.path.abspath(dest)):
                    _release_lock(session_id, os.path.abspath(source))
                    return f"Destination resource is being used by another session. Wait."
                
                if os.path.isdir(source):
                    shutil.copytree(source, dest, dirs_exist_ok=True)
                    result = f"Directory '{source}' copied to '{dest}'"
                else:
                    shutil.copy2(source, dest)
                    result = f"File '{source}' copied to '{dest}'"
                
                _release_lock(session_id, os.path.abspath(source))
                _release_lock(session_id, os.path.abspath(dest))
                return result
            except OSError as e:
                _release_lock(session_id, os.path.abspath(source))
                _release_lock(session_id, os.path.abspath(dest))
                return f"Error: {str(e)}"

        elif cmd == "mv":
            if len(args) < 2:
                # Use file dialog to select source and destination
                from file_creation_dialog import FileCreationDialog
                dialog = FileCreationDialog()
                
                # Select source
                success, source, message = dialog.select_file_or_folder("Select file/folder to move", allow_files=True, allow_folders=True)
                if not success:
                    return message
                
                # Select destination
                success, dest, message = dialog.select_destination(source, "move")
                if not success:
                    return message
            else:
                source, dest = args[0], args[1]
            
            if not os.path.exists(source):
                return f"Error: {source} does not exist"
            
            try:
                # Check for locks on both source and destination
                locked_by = _check_lock(session_id, os.path.abspath(source))
                if locked_by:
                    return f"Source resource is being used by another session. Wait."
                
                locked_by = _check_lock(session_id, os.path.abspath(dest))
                if locked_by:
                    return f"Destination resource is being used by another session. Wait."
                
                # Acquire locks
                if not _acquire_lock(session_id, os.path.abspath(source)):
                    return f"Source resource is being used by another session. Wait."
                if not _acquire_lock(session_id, os.path.abspath(dest)):
                    _release_lock(session_id, os.path.abspath(source))
                    return f"Destination resource is being used by another session. Wait."
                
                shutil.move(source, dest)
                _release_lock(session_id, os.path.abspath(source))
                _release_lock(session_id, os.path.abspath(dest))
                return f"Moved '{source}' to '{dest}'"
            except OSError as e:
                _release_lock(session_id, os.path.abspath(source))
                _release_lock(session_id, os.path.abspath(dest))
                return f"Error: {str(e)}"

        elif cmd == "cat":
            if not args:
                return "Usage: cat <file>"
            target = args[0]
            if not os.path.exists(target):
                return f"Error: {target} does not exist"
            if not os.path.isfile(target):
                return f"Error: {target} is not a file"
            
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                try:
                    with open(target, 'r', encoding='latin-1') as f:
                        return f.read()
                except Exception as e:
                    return f"Error reading file: {str(e)}"
            except Exception as e:
                return f"Error: {str(e)}"

        elif cmd == "edit":
            if not args:
                return "Usage: edit <file>"
            target = args[0]
            try:
                # Check for lock
                locked_by = _check_lock(session_id, os.path.abspath(target))
                if locked_by:
                    return f"Resource is being used by another session. Wait."
                
                # Acquire lock
                if not _acquire_lock(session_id, os.path.abspath(target)):
                    return f"Resource is being used by another session. Wait."
                
                # Simple text editor simulation
                if os.path.exists(target):
                    with open(target, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    content = ""
                
                print(f"Editing {target} (type 'SAVE' on a new line to save and exit):")
                print("-" * 50)
                print(content)
                print("-" * 50)
                
                new_content = []
                while True:
                    line = input("> ")
                    if line.strip() == "SAVE":
                        break
                    new_content.append(line)
                
                with open(target, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_content))
                
                _release_lock(session_id, os.path.abspath(target))
                return f"File '{target}' saved"
            except Exception as e:
                _release_lock(session_id, os.path.abspath(target))
                return f"Error: {str(e)}"

        elif cmd == "cpu":
            # Get CPU usage percentage
            cpu_percent = psutil.cpu_percent(interval=1)
            return f"CPU Usage: {cpu_percent}%"

        elif cmd == "mem":
            # Get memory usage
            memory = psutil.virtual_memory()
            return f"Memory Usage: {memory.percent}% ({memory.used // (1024*1024)} MB / {memory.total // (1024*1024)} MB)"

        elif cmd == "ps":
            # List running processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    processes.append(f"{proc.info['pid']:6} {proc.info['name']:<20} {proc.info['username']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            if processes:
                header = f"{'PID':6} {'Name':<20} {'User'}"
                return header + "\n" + "\n".join(processes)
            else:
                return "No processes found"

        elif cmd == "find":
            if not args:
                return "Usage: find <path> <name_pattern>"
            if len(args) < 2:
                return "Usage: find <path> <name_pattern>"
            search_path, pattern = args[0], args[1]
            if not os.path.exists(search_path):
                return f"Error: {search_path} does not exist"
            
            results = []
            try:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if pattern in file:
                            results.append(os.path.join(root, file))
                    for dir_name in dirs:
                        if pattern in dir_name:
                            results.append(os.path.join(root, dir_name))
                
                if results:
                    return "\n".join(results)
                else:
                    return f"No files or directories matching '{pattern}' found"
            except Exception as e:
                return f"Error: {str(e)}"

        elif cmd == "grep":
            if len(args) < 2:
                return "Usage: grep <pattern> <file>"
            pattern, file_path = args[0], args[1]
            if not os.path.exists(file_path):
                return f"Error: {file_path} does not exist"
            if not os.path.isfile(file_path):
                return f"Error: {file_path} is not a file"
            
            try:
                matches = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern in line:
                            matches.append(f"{file_path}:{line_num}: {line.strip()}")
                
                if matches:
                    return "\n".join(matches)
                else:
                    return f"Pattern '{pattern}' not found in {file_path}"
            except Exception as e:
                return f"Error: {str(e)}"

        elif cmd == "clear":
            # Clear screen (works on both Windows and Unix)
            os.system('cls' if os.name == 'nt' else 'clear')
            return ""

        elif cmd == "echo":
            # Echo command
            return " ".join(args) if args else ""

        elif cmd == "date":
            # Show current date and time
            import datetime
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        elif cmd == "whoami":
            # Show current user
            import getpass
            return getpass.getuser()

        elif cmd == "uname":
            # Show system information
            import platform
            return f"{platform.system()} {platform.release()} {platform.machine()}"

        elif cmd == "df":
            # Show disk usage
            try:
                disk_usage = psutil.disk_usage('.')
                total = disk_usage.total // (1024**3)  # GB
                used = disk_usage.used // (1024**3)    # GB
                free = disk_usage.free // (1024**3)    # GB
                percent = (disk_usage.used / disk_usage.total) * 100
                return f"Filesystem      Size  Used  Avail  Use%\n/dev/disk        {total:3d}G  {used:3d}G  {free:3d}G  {percent:4.1f}%"
            except Exception as e:
                return f"Error: {str(e)}"

        else:
            # Try to run as shell command
            try:
                result = subprocess.run([cmd] + args, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    return f"Error: {result.stderr.strip()}"
            except subprocess.TimeoutExpired:
                return "Error: Command timed out"
            except FileNotFoundError:
                return "Command not found"
            except Exception as e:
                return f"Error: {str(e)}"

    except Exception as e:
        return f"Error: {str(e)}"
