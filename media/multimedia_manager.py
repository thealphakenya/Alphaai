import os
import json
from typing import Dict, List, Optional, Any

class MultimediaManager:
    """Manages multimedia content display and playback."""
    
    def __init__(self, media_dir: str = "media"):
        self.media_dir = media_dir
        self.videos_dir = os.path.join(media_dir, "videos")
        self.audio_dir = os.path.join(media_dir, "audio")
        self.images_dir = os.path.join(media_dir, "images")
        self.documents_dir = os.path.join(media_dir, "documents")
        
        # Create directories if they don't exist
        for directory in [self.media_dir, self.videos_dir, 
                         self.audio_dir, self.images_dir, self.documents_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Media registry
        self.media_registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load media registry from file."""
        registry_path = os.path.join(self.media_dir, "registry.json")
        if os.path.exists(registry_path):
            try:
                with open(registry_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading media registry: {e}")
        
        # Initialize empty registry if not found
        return {
            "videos": {},
            "audio": {},
            "images": {},
            "documents": {}
        }
    
    def _save_registry(self):
        """Save media registry to file."""
        registry_path = os.path.join(self.media_dir, "registry.json")
        try:
            with open(registry_path, 'w') as f:
                json.dump(self.media_registry, f, indent=2)
        except Exception as e:
            print(f"Error saving media registry: {e}")
    
    def register_media(self, media_type: str, media_id: str, metadata: Dict):
        """Register a media file in the registry."""
        if media_type not in ["videos", "audio", "images", "documents"]:
            return {"status": "error", "message": f"Invalid media type: {media_type}"}
        
        # Add to registry
        self.media_registry[media_type][media_id] = metadata
        self._save_registry()
        
        return {"status": "success", "message": f"{media_type.capitalize()} registered successfully"}
    
    def get_media_info(self, media_type: str, media_id: str) -> Optional[Dict]:
        """Get information about a media file."""
        if media_type not in ["videos", "audio", "images", "documents"]:
            return None
        
        return self.media_registry[media_type].get(media_id)
    
    def get_media_url(self, media_type: str, media_id: str) -> Optional[str]:
        """Get the URL for a media file."""
        media_info = self.get_media_info(media_type, media_id)
        if not media_info:
            return None
        
        return media_info.get("url")
    
    def search_media(self, query: str, media_type: Optional[str] = None) -> List[Dict]:
        """Search for media files by query."""
        results = []
        
        # Determine which media types to search
        media_types = [media_type] if media_type else ["videos", "audio", "images", "documents"]
        
        for mtype in media_types:
            if mtype not in self.media_registry:
                continue
                
            for media_id, metadata in self.media_registry[mtype].items():
                # Search in title, description, and tags
                title = metadata.get("title", "").lower()
                description = metadata.get("description", "").lower()
                tags = metadata.get("tags", [])
                
                if (query.lower() in title or 
                    query.lower() in description or 
                    query.lower() in " ".join(tags).lower()):
                    
                    results.append({
                        "id": media_id,
                        "type": mtype,
                        "title": metadata.get("title", "Untitled"),
                        "thumbnail": metadata.get("thumbnail"),
                        "duration": metadata.get("duration")
                    })
        
        return results
    
    def get_media_player_config(self, media_type: str, media_id: str) -> Dict:
        """Get configuration for media player."""
        media_info = self.get_media_info(media_type, media_id)
        if not media_info:
            return {"status": "error", "message": "Media not found"}
        
        if media_type == "videos":
            return {
                "type": "video",
                "url": media_info.get("url"),
                "title": media_info.get("title", "Untitled"),
                "poster": media_info.get("thumbnail"),
                "subtitles": media_info.get("subtitles", []),
                "autoplay": False
            }
        elif media_type == "audio":
            return {
                "type": "audio",
                "url": media_info.get("url"),
                "title": media_info.get("title", "Untitled"),
                "artwork": media_info.get("artwork"),
                "artist": media_info.get("artist", "Unknown"),
                "autoplay": False
            }
        elif media_type == "images":
            return {
                "type": "image",
                "url": media_info.get("url"),
                "title": media_info.get("title", "Untitled"),
                "alt": media_info.get("description", "Image")
            }
        elif media_type == "documents":
            return {
                "type": "document",
                "url": media_info.get("url"),
                "title": media_info.get("title", "Untitled"),
                "fileType": media_info.get("fileType", "pdf")
            }
        
        return {"status": "error", "message": "Unsupported media type"}
