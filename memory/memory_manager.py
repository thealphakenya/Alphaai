import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

class MemoryManager:
    """Manages persistent memory for the AI, including conversations and user data."""
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = memory_dir
        self.conversations_dir = os.path.join(memory_dir, "conversations")
        self.users_dir = os.path.join(memory_dir, "users")
        self.workspace_dir = os.path.join(memory_dir, "workspace")
        self.projects_dir = os.path.join(memory_dir, "projects")
        
        # Create directories if they don't exist
        for directory in [self.memory_dir, self.conversations_dir, 
                          self.users_dir, self.workspace_dir, self.projects_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # In-memory cache
        self.conversation_cache = {}
        self.user_cache = {}
        self.project_cache = {}
    
    def save_conversation(self, conversation_id: str, messages: List[Dict], metadata: Dict = None):
        """Save a conversation to persistent storage."""
        if not metadata:
            metadata = {}
        
        # Add timestamp if not present
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.now().isoformat()
        
        conversation_data = {
            "id": conversation_id,
            "messages": messages,
            "metadata": metadata
        }
        
        # Save to cache
        self.conversation_cache[conversation_id] = conversation_data
        
        # Save to file
        conversation_path = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        with open(conversation_path, 'w') as f:
            json.dump(conversation_data, f, indent=2)
        
        return {"status": "success", "message": "Conversation saved"}
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Retrieve a conversation by ID."""
        # Check cache first
        if conversation_id in self.conversation_cache:
            return self.conversation_cache[conversation_id]
        
        # Check file system
        conversation_path = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        if os.path.exists(conversation_path):
            with open(conversation_path, 'r') as f:
                conversation_data = json.load(f)
                # Update cache
                self.conversation_cache[conversation_id] = conversation_data
                return conversation_data
        
        return None
    
    def save_user_data(self, user_id: str, user_data: Dict):
        """Save user data to persistent storage."""
        # Add timestamp if not present
        if "last_updated" not in user_data:
            user_data["last_updated"] = datetime.now().isoformat()
        
        # Save to cache
        self.user_cache[user_id] = user_data
        
        # Save to file
        user_path = os.path.join(self.users_dir, f"{user_id}.json")
        with open(user_path, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        return {"status": "success", "message": "User data saved"}
    
    def get_user_data(self, user_id: str) -> Optional[Dict]:
        """Retrieve user data by ID."""
        # Check cache first
        if user_id in self.user_cache:
            return self.user_cache[user_id]
        
        # Check file system
        user_path = os.path.join(self.users_dir, f"{user_id}.json")
        if os.path.exists(user_path):
            with open(user_path, 'r') as f:
                user_data = json.load(f)
                # Update cache
                self.user_cache[user_id] = user_data
                return user_data
        
        return None
    
    def save_project_data(self, project_id: str, project_data: Dict):
        """Save project data to persistent storage."""
        # Add timestamp if not present
        if "last_updated" not in project_data:
            project_data["last_updated"] = datetime.now().isoformat()
        
        # Create project directory if it doesn't exist
        project_dir = os.path.join(self.projects_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # Save metadata
        metadata_path = os.path.join(project_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        # Save to cache
        self.project_cache[project_id] = project_data
        
        return {"status": "success", "message": "Project data saved"}
    
    def get_project_data(self, project_id: str) -> Optional[Dict]:
        """Retrieve project data by ID."""
        # Check cache first
        if project_id in self.project_cache:
            return self.project_cache[project_id]
        
        # Check file system
        metadata_path = os.path.join(self.projects_dir, project_id, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                project_data = json.load(f)
                # Update cache
                self.project_cache[project_id] = project_data
                return project_data
        
        return None
    
    def save_workspace_state(self, workspace_id: str, state: Dict):
        """Save workspace state to persistent storage."""
        workspace_dir = os.path.join(self.workspace_dir, workspace_id)
        os.makedirs(workspace_dir, exist_ok=True)
        
        state_path = os.path.join(workspace_dir, "state.json")
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)
        
        return {"status": "success", "message": "Workspace state saved"}
    
    def get_workspace_state(self, workspace_id: str) -> Optional[Dict]:
        """Retrieve workspace state by ID."""
        state_path = os.path.join(self.workspace_dir, workspace_id, "state.json")
        if os.path.exists(state_path):
            with open(state_path, 'r') as f:
                return json.load(f)
        
        return None
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict]:
        """Search conversations for a query string."""
        results = []
        
        # List all conversation files
        conversation_files = os.listdir(self.conversations_dir)
        
        for file_name in conversation_files:
            if not file_name.endswith('.json'):
                continue
                
            file_path = os.path.join(self.conversations_dir, file_name)
            try:
                with open(file_path, 'r') as f:
                    conversation = json.load(f)
                
                # Simple search in messages
                found = False
                for message in conversation.get("messages", []):
                    if query.lower() in message.get("content", "").lower():
                        found = True
                        break
                
                if found:
                    results.append({
                        "id": conversation.get("id"),
                        "preview": conversation.get("messages", [])[0].get("content", "")[:100] if conversation.get("messages") else "",
                        "timestamp": conversation.get("metadata", {}).get("timestamp")
                    })
                    
                    if len(results) >= limit:
                        break
                        
            except Exception as e:
                print(f"Error searching conversation {file_name}: {e}")
        
        # Sort by timestamp, newest first
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return results
    
    def backup_to_github(self, github_repo: str, github_token: str):
        """Backup all memory data to GitHub repository."""
        # This would be implemented with GitHub API or git commands
        # For now, we'll just simulate the backup process
        print(f"Backing up memory to GitHub repository: {github_repo}")
        time.sleep(2)  # Simulate backup time
        return {"status": "success", "message": "Memory backed up to GitHub"}
