import os
import json
from typing import Dict, List, Optional, Any

class WorkspaceManager:
    """Manages adaptive workspace UI and tools based on current task."""
    
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = workspace_dir
        self.templates_dir = os.path.join(workspace_dir, "templates")
        self.active_workspaces = {}
        
        # Create directories if they don't exist
        os.makedirs(self.workspace_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Load workspace templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load workspace templates from files."""
        templates = {}
        
        # Default templates if none exist
        default_templates = {
            "coding": {
                "name": "Coding Workspace",
                "description": "Workspace for software development",
                "tools": ["code_editor", "terminal", "file_explorer", "git_panel"],
                "layout": "split",
                "theme": "dark",
                "panels": [
                    {"id": "editor", "type": "code_editor", "position": "main"},
                    {"id": "terminal", "type": "terminal", "position": "bottom"},
                    {"id": "files", "type": "file_explorer", "position": "left"},
                    {"id": "git", "type": "git_panel", "position": "right"}
                ]
            },
            "writing": {
                "name": "Writing Workspace",
                "description": "Workspace for content creation",
                "tools": ["text_editor", "research_panel", "outline_tool"],
                "layout": "focused",
                "theme": "light",
                "panels": [
                    {"id": "editor", "type": "text_editor", "position": "main"},
                    {"id": "research", "type": "research_panel", "position": "right"},
                    {"id": "outline", "type": "outline_tool", "position": "left"}
                ]
            },
            "animation": {
                "name": "Animation Workspace",
                "description": "Workspace for creating animations",
                "tools": ["timeline", "canvas", "asset_library", "preview_panel"],
                "layout": "complex",
                "theme": "dark",
                "panels": [
                    {"id": "canvas", "type": "canvas", "position": "main"},
                    {"id": "timeline", "type": "timeline", "position": "bottom"},
                    {"id": "assets", "type": "asset_library", "position": "left"},
                    {"id": "preview", "type": "preview_panel", "position": "right"}
                ]
            },
            "music": {
                "name": "Music Production",
                "description": "Workspace for music and audio production",
                "tools": ["track_editor", "mixer", "instrument_panel", "audio_library"],
                "layout": "complex",
                "theme": "dark",
                "panels": [
                    {"id": "tracks", "type": "track_editor", "position": "main"},
                    {"id": "mixer", "type": "mixer", "position": "bottom"},
                    {"id": "instruments", "type": "instrument_panel", "position": "left"},
                    {"id": "library", "type": "audio_library", "position": "right"}
                ]
            },
            "default": {
                "name": "Default Workspace",
                "description": "General purpose workspace",
                "tools": ["chat", "file_viewer", "media_player"],
                "layout": "simple",
                "theme": "light",
                "panels": [
                    {"id": "chat", "type": "chat", "position": "main"},
                    {"id": "files", "type": "file_viewer", "position": "left"},
                    {"id": "media", "type": "media_player", "position": "right"}
                ]
            }
        }
        
        # Check if template files exist
        template_files = os.listdir(self.templates_dir) if os.path.exists(self.templates_dir) else []
        
        if not template_files:
            # Save default templates
            for template_id, template in default_templates.items():
                template_path = os.path.join(self.templates_dir, f"{template_id}.json")
                with open(template_path, 'w') as f:
                    json.dump(template, f, indent=2)
            
            templates = default_templates
        else:
            # Load templates from files
            for file_name in template_files:
                if not file_name.endswith('.json'):
                    continue
                    
                template_id = file_name.replace('.json', '')
                template_path = os.path.join(self.templates_dir, file_name)
                
                try:
                    with open(template_path, 'r') as f:
                        templates[template_id] = json.load(f)
                except Exception as e:
                    print(f"Error loading template {template_id}: {e}")
        
        return templates
    
    def create_workspace(self, workspace_id: str, template_id: str = "default") -> Dict:
        """Create a new workspace based on a template."""
        if template_id not in self.templates:
            return {"status": "error", "message": f"Template not found: {template_id}"}
        
        # Create workspace based on template
        template = self.templates[template_id]
        workspace = {
            "id": workspace_id,
            "name": template.get("name", "Workspace"),
            "template": template_id,
            "tools": template.get("tools", []),
            "layout": template.get("layout", "simple"),
            "theme": template.get("theme", "light"),
            "panels": template.get("panels", []),
            "state": {
                "active_panel": "main",
                "panel_sizes": {},
                "tool_states": {}
            }
        }
        
        # Save workspace
        workspace_path = os.path.join(self.workspace_dir, f"{workspace_id}.json")
        with open(workspace_path, 'w') as f:
            json.dump(workspace, f, indent=2)
        
        # Add to active workspaces
        self.active_workspaces[workspace_id] = workspace
        
        return {"status": "success", "message": "Workspace created", "workspace": workspace}
    
    def get_workspace(self, workspace_id: str) -> Optional[Dict]:
        """Get workspace configuration."""
        # Check active workspaces first
        if workspace_id in self.active_workspaces:
            return self.active_workspaces[workspace_id]
        
        # Check file system
        workspace_path = os.path.join(self.workspace_dir, f"{workspace_id}.json")
        if os.path.exists(workspace_path):
            try:
                with open(workspace_path, 'r') as f:
                    workspace = json.load(f)
                    # Add to active workspaces
                    self.active_workspaces[workspace_id] = workspace
                    return workspace
            except Exception as e:
                print(f"Error loading workspace {workspace_id}: {e}")
        
        return None
    
    def update_workspace(self, workspace_id: str, updates: Dict) -> Dict:
        """Update workspace configuration."""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return {"status": "error", "message": f"Workspace not found: {workspace_id}"}
        
        # Update workspace properties
        for key, value in updates.items():
            if key in workspace and key != "id":
                workspace[key] = value
        
        # Save updated workspace
        workspace_path = os.path.join(self.workspace_dir, f"{workspace_id}.json")
        with open(workspace_path, 'w') as f:
            json.dump(workspace, f, indent=2)
        
        # Update active workspaces
        self.active_workspaces[workspace_id] = workspace
        
        return {"status": "success", "message": "Workspace updated", "workspace": workspace}
    
    def switch_workspace_template(self, workspace_id: str, template_id: str) -> Dict:
        """Switch workspace to a different template."""
        if template_id not in self.templates:
            return {"status": "error", "message": f"Template not found: {template_id}"}
        
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return {"status": "error", "message": f"Workspace not found: {workspace_id}"}
        
        # Get template
        template = self.templates[template_id]
        
        # Update workspace with template properties
        workspace["template"] = template_id
        workspace["tools"] = template.get("tools", [])
        workspace["layout"] = template.get("layout", "simple")
        workspace["theme"] = template.get("theme", "light")
        workspace["panels"] = template.get("panels", [])
        
        # Preserve workspace ID and name
        workspace_name = workspace.get("name", "Workspace")
        
        # Save updated workspace
        workspace_path = os.path.join(self.workspace_dir, f"{workspace_id}.json")
        with open(workspace_path, 'w') as f:
            json.dump(workspace, f, indent=2)
        
        # Update active workspaces
        self.active_workspaces[workspace_id] = workspace
        
        return {"status": "success", "message": "Workspace template switched", "workspace": workspace}
    
    def detect_appropriate_template(self, task_description: str) -> str:
        """Detect the most appropriate workspace template based on task description."""
        # Simple keyword-based detection
        task_lower = task_description.lower()
        
        if any(keyword in task_lower for keyword in ["code", "program", "develop", "script", "debug"]):
            return "coding"
        elif any(keyword in task_lower for keyword in ["write", "blog", "article", "story", "script"]):
            return "writing"
        elif any(keyword in task_lower for keyword in ["animate", "animation", "motion", "video"]):
            return "animation"
        elif any(keyword in task_lower for keyword in ["music", "song", "audio", "sound", "compose"]):
            return "music"
        
        # Default template if no match
        return "default"
