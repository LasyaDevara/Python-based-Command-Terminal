# Python Terminal

A multi-session command terminal with history persistence built in Python.

## Features

- **Multi-session support**: Create and manage multiple terminal sessions
- **Command history**: Persistent command history for each session stored in JSON format
- **System monitoring**: CPU, memory, and process monitoring using psutil
- **File system operations**: Basic file and directory operations
- **Clean architecture**: Modular design for easy extension and future web UI integration

## Commands

### Session Management
- `newterm` - Start a new terminal session
- `sessions` - List all existing sessions
- `switch <id>` - Switch to another session
- `history` - Show command history of current session

### File System Operations
- `pwd` - Print working directory
- `ls [path]` - List directory contents
- `cd <directory>` - Change directory
- `mkdir <directory>` - Create directory
- `rm <file>` - Remove file

### System Monitoring
- `cpu` - Show CPU usage percentage
- `mem` - Show memory usage information
- `ps` - Show running processes

### Other
- `help` - Show available commands
- `exit` - Quit the terminal

## Installation

1. Ensure Python 3.9+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the terminal:
```bash
python main.py
```

## Project Structure

- `main.py` - Main CLI loop and command handling
- `session_manager.py` - Session creation, switching, and management
- `history.py` - Command history persistence in JSON format
- `terminal.py` - Command execution logic
- `utils.py` - Helper utilities and error handling

## Data Storage

Session data and command history are stored in:
- `data/sessions/` - Individual session history files (JSON format)
- `data/current_session.txt` - Tracks the current active session

## Error Handling

The terminal provides comprehensive error handling:
- Invalid commands show "Command not found"
- File system errors show specific error messages
- Command timeouts are handled gracefully
- Session switching validates session existence

## Future Extensions

The modular design allows for easy extension to:
- Web-based UI
- Additional commands
- Enhanced formatting with rich library
- Remote session management
- Command completion
- Syntax highlighting
