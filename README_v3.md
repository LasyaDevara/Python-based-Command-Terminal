# Python Terminal v3.0 - Smart AI-Assisted Multi-Session Terminal

A powerful, intelligent terminal application that combines traditional command-line functionality with AI-powered natural language processing and multi-session management.

## 🚀 Features

### Multi-Session Support
- **Create new sessions**: `newterm` - Start a new terminal session
- **List sessions**: `sessions` - View all available sessions with details
- **Switch sessions**: `switch <session_id>` - Switch between sessions
- **Persistent history**: Each session maintains its own command history
- **Working directory tracking**: Sessions remember their working directories

### AI-Powered Natural Language Processing
- **Natural language commands**: Type what you want to do in plain English
- **Smart interpretation**: AI converts natural language to terminal commands
- **Chat mode**: `chat` - Enter conversational mode for extended AI interaction
- **Auto-confirmation**: Commands are executed automatically after AI interpretation

### File and Folder Operations
- **Complete file management**: `pwd`, `ls`, `cd`, `mkdir`, `touch`, `rm`, `cp`, `mv`
- **File editing**: `edit <file>` - Simple text editor
- **File searching**: `find <path> <pattern>`, `grep <pattern> <file>`
- **Resource locking**: Prevents conflicts between sessions when modifying files
- **Windows compatibility**: Full support for Windows file operations

### System Information
- **Process monitoring**: `ps` - Show running processes
- **System resources**: `cpu`, `mem`, `df` - Monitor system usage
- **System info**: `date`, `whoami`, `uname` - Get system information
- **Real-time data**: Live system monitoring capabilities

### Smart Command Parsing
- **Automatic detection**: Distinguishes between terminal commands and natural language
- **Shell command support**: Executes native shell commands
- **Intelligent suggestions**: Provides command suggestions and auto-completion
- **Error handling**: Graceful error handling and user feedback

## 📋 Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Ollama** (for AI features):
   - Download from [ollama.ai](https://ollama.ai)
   - Install and run Ollama
   - Pull a model: `ollama pull llama2`

3. **Run the terminal**:
   ```bash
   python main.py
   ```

## 🎯 Usage Examples

### Basic Commands
```bash
# Traditional terminal commands
ls                          # List files
cd /path/to/directory       # Change directory
mkdir new_folder            # Create directory
touch new_file.txt          # Create file
rm old_file.txt             # Remove file
```

### Natural Language Commands
```bash
# AI interprets natural language
create a new folder called test
show me the current directory
what is the CPU usage?
list all files in current folder
move file1.txt to the test folder
find all Python files
search for 'hello' in main.py
```

### Session Management
```bash
newterm                     # Create new session
sessions                    # List all sessions
switch session_2            # Switch to session_2
history                     # Show command history
```

### AI Chat Mode
```bash
chat                        # Enter AI chat mode
# Then type natural language commands
create a new file called config.txt
show me running processes
what time is it?
```

## 🔧 Advanced Features

### Resource Locking
- Files and folders are automatically locked when being modified
- Other sessions see: "Resource is being used by another session. Wait."
- Locks expire after 5 minutes to prevent deadlocks

### Session Persistence
- All sessions are saved to `data/sessions/`
- Command history is preserved between terminal restarts
- Working directories are maintained per session

### Help System
- `help` - Show comprehensive help
- `help <command>` - Get detailed help for specific command
- Rich formatting with examples and troubleshooting

## 📁 Project Structure

```
python_terminal/
├── main.py                 # Main application entry point
├── terminal.py             # Command execution engine
├── session_manager.py      # Multi-session management
├── command_parser.py       # Smart command parsing
├── ai_interpreter.py       # AI natural language processing
├── chat_interface.py       # AI chat mode interface
├── help_system.py          # Comprehensive help system
├── enhanced_history.py     # Advanced history management
├── history.py              # Basic history functions
├── utils.py                # Utility functions
├── data/
│   ├── sessions/           # Session data storage
│   └── resource_locks.json # Resource locking data
└── requirements.txt        # Python dependencies
```

## 🎨 User Interface

- **Rich formatting**: Beautiful terminal output with colors and formatting
- **Progress indicators**: Visual feedback for long-running operations
- **Error handling**: Clear error messages and suggestions
- **Session info**: Current session, command count, and working directory display

## 🔒 Security Features

- **Resource locking**: Prevents file conflicts between sessions
- **Safe file operations**: Error handling for all file operations
- **Session isolation**: Each session operates independently
- **Input validation**: Comprehensive input validation and sanitization

## 🚀 Getting Started

1. **Start the terminal**:
   ```bash
   python main.py
   ```

2. **Try natural language**:
   ```
   [session_1] >>> create a new folder called my_project
   ```

3. **Use traditional commands**:
   ```
   [session_1] >>> ls
   [session_1] >>> cd my_project
   ```

4. **Enter chat mode**:
   ```
   [session_1] >>> chat
   ```

5. **Get help**:
   ```
   [session_1] >>> help
   ```

## 🐛 Troubleshooting

- **AI not working**: Ensure Ollama is installed and running
- **Resource locked**: Wait a few minutes or check which session is using the resource
- **Command not found**: Try natural language or check `help` for available commands
- **Session issues**: Use `sessions` to see available sessions

## 📝 Requirements

- Python 3.7+
- Windows 10+ (also works on Linux/macOS)
- Ollama (for AI features)
- Rich (for terminal formatting)
- psutil (for system monitoring)

## 🤝 Contributing

This is a complete, production-ready terminal application. All features are implemented and tested.

## 📄 License

This project is ready for use and distribution.

---

**Python Terminal v3.0** - The smart way to interact with your system! 🚀
