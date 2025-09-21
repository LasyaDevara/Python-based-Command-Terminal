#!/usr/bin/env python3
"""
Manage multiple terminal sessions with working directory tracking
"""

import os
import json
from history import load_history, save_history

class SessionManager:
    def __init__(self):
        """Initialize session manager"""
        self.sessions_dir = "data/sessions"
        self.current_session_file = "data/current_session.txt"
        self.session_info_file = "data/session_info.json"
        os.makedirs(self.sessions_dir, exist_ok=True)
        self._ensure_current_session_exists()
        self._load_session_info()
    
    def _ensure_current_session_exists(self):
        """Ensure current session file exists"""
        if not os.path.exists(self.current_session_file):
            # Create first session
            self.create_new_session()
    
    def _load_session_info(self):
        """Load session information from file"""
        try:
            if os.path.exists(self.session_info_file):
                with open(self.session_info_file, 'r') as f:
                    self.session_info = json.load(f)
            else:
                self.session_info = {}
        except (json.JSONDecodeError, IOError):
            self.session_info = {}
    
    def _save_session_info(self):
        """Save session information to file"""
        try:
            with open(self.session_info_file, 'w') as f:
                json.dump(self.session_info, f)
        except IOError:
            pass
    
    def get_current_session(self):
        """Get the current session ID - create unique session for each terminal instance"""
        try:
            # Check if we already have a session for this process
            process_id = os.getpid()
            process_session_file = f"data/process_{process_id}_session.txt"
            
            if os.path.exists(process_session_file):
                with open(process_session_file, 'r') as f:
                    return f.read().strip()
            else:
                # Create a new unique session for this process
                return self._create_unique_session_for_process(process_id)
        except Exception:
            # Fallback to creating a new session
            return self._create_unique_session_for_process(os.getpid())
    
    def _create_unique_session_for_process(self, process_id):
        """Create a unique session for the current process"""
        # Generate a unique session ID based on process ID and timestamp
        import time
        timestamp = int(time.time())
        session_id = f"session_{process_id}_{timestamp}"
        
        # Create session directory and initialize history
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        with open(session_file, 'w') as f:
            json.dump([], f)
        
        # Initialize session info
        self.session_info[session_id] = {
            'working_directory': os.getcwd(),
            'created_at': self._get_timestamp(),
            'last_accessed': self._get_timestamp(),
            'process_id': process_id
        }
        self._save_session_info()
        
        # Save process session file
        process_session_file = f"data/process_{process_id}_session.txt"
        with open(process_session_file, 'w') as f:
            f.write(session_id)
        
        return session_id
    
    def create_new_session(self):
        """Create a new session and return its ID"""
        sessions = self.list_sessions()
        session_id = f"session_{len(sessions) + 1}"
        
        # Create session directory and initialize history
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        with open(session_file, 'w') as f:
            json.dump([], f)
        
        # Initialize session info
        self.session_info[session_id] = {
            'working_directory': os.getcwd(),
            'created_at': self._get_timestamp(),
            'last_accessed': self._get_timestamp()
        }
        self._save_session_info()
        
        # Set as current session
        with open(self.current_session_file, 'w') as f:
            f.write(session_id)
        
        return session_id
    
    def list_sessions(self):
        """List all existing sessions with details"""
        sessions = []
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                session_id = filename[:-5]  # Remove .json extension
                sessions.append(session_id)
        sessions.sort()  # Sort for consistent ordering
        return sessions
    
    def get_session_details(self, session_id=None):
        """Get detailed information about sessions"""
        if session_id is None:
            session_id = self.get_current_session()
        
        if session_id not in self.session_info:
            return None
        
        info = self.session_info[session_id].copy()
        
        # Add history count
        history = load_history(session_id)
        info['command_count'] = len(history)
        
        # Add working directory status
        if os.path.exists(info['working_directory']):
            info['working_directory_status'] = 'valid'
        else:
            info['working_directory_status'] = 'invalid'
            info['working_directory'] = os.getcwd()  # Reset to current directory
        
        return info
    
    def switch_session(self, session_id):
        """Switch to another session"""
        sessions = self.list_sessions()
        if session_id in sessions:
            # Update last accessed time
            if session_id in self.session_info:
                self.session_info[session_id]['last_accessed'] = self._get_timestamp()
                self._save_session_info()
            
            # Change to session's working directory if valid
            session_info = self.get_session_details(session_id)
            if session_info and session_info['working_directory_status'] == 'valid':
                try:
                    os.chdir(session_info['working_directory'])
                except OSError:
                    pass  # Stay in current directory if can't change
            
            with open(self.current_session_file, 'w') as f:
                f.write(session_id)
            return True
        return False
    
    def update_working_directory(self, session_id, new_directory):
        """Update the working directory for a session"""
        if session_id in self.session_info:
            self.session_info[session_id]['working_directory'] = new_directory
            self.session_info[session_id]['last_accessed'] = self._get_timestamp()
            self._save_session_info()
    
    def get_working_directory(self, session_id=None):
        """Get the working directory for a session"""
        if session_id is None:
            session_id = self.get_current_session()
        
        if session_id in self.session_info:
            return self.session_info[session_id]['working_directory']
        return os.getcwd()
    
    def cleanup_old_sessions(self, days=30):
        """Clean up sessions older than specified days"""
        import time
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        
        sessions_to_remove = []
        for session_id, info in self.session_info.items():
            if info.get('last_accessed', 0) < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            # Remove session file
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            if os.path.exists(session_file):
                os.remove(session_file)
            
            # Remove from session info
            del self.session_info[session_id]
        
        if sessions_to_remove:
            self._save_session_info()
            return len(sessions_to_remove)
        
        return 0
    
    def _get_timestamp(self):
        """Get current timestamp"""
        import time
        return time.time()
    
    def get_session_stats(self):
        """Get statistics about all sessions"""
        stats = {
            'total_sessions': len(self.session_info),
            'active_sessions': 0,
            'total_commands': 0,
            'oldest_session': None,
            'newest_session': None
        }
        
        if not self.session_info:
            return stats
        
        timestamps = []
        for session_id, info in self.session_info.items():
            # Count commands
            history = load_history(session_id)
            stats['total_commands'] += len(history)
            
            # Track timestamps
            created_at = info.get('created_at', 0)
            last_accessed = info.get('last_accessed', 0)
            timestamps.append((session_id, created_at, last_accessed))
            
            # Check if session is active (accessed within last hour)
            import time
            if last_accessed > time.time() - 3600:
                stats['active_sessions'] += 1
        
        if timestamps:
            # Find oldest and newest sessions
            oldest = min(timestamps, key=lambda x: x[1])
            newest = max(timestamps, key=lambda x: x[1])
            stats['oldest_session'] = oldest[0]
            stats['newest_session'] = newest[0]
        
        return stats
    
    def cleanup_process_session(self):
        """Clean up process session file when terminal exits"""
        try:
            process_id = os.getpid()
            process_session_file = f"data/process_{process_id}_session.txt"
            if os.path.exists(process_session_file):
                os.remove(process_session_file)
        except Exception:
            pass
