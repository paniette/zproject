"""
Map manager for saving/loading maps as JSON files
"""
import json
import os
from pathlib import Path
from django.conf import settings
from .utils import ensure_directory
import uuid
from datetime import datetime


class MapManager:
    """Manage map files (JSON) for users"""
    
    def __init__(self, username='temp'):
        self.username = username
        self.user_maps_dir = Path(settings.USERS_DIR) / username / 'maps'
        ensure_directory(self.user_maps_dir)
    
    def create_map(self, map_data):
        """Create a new map"""
        map_id = map_data.get('id') or f"map_{uuid.uuid4().hex[:12]}"
        map_data['id'] = map_id
        
        # Ensure metadata
        if 'metadata' not in map_data:
            map_data['metadata'] = {}
        
        map_data['metadata']['created'] = datetime.now().isoformat()
        map_data['metadata']['modified'] = datetime.now().isoformat()
        map_data['metadata']['author'] = self.username
        
        map_file = self.user_maps_dir / f"{map_id}.json"
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(map_data, f, indent=2, ensure_ascii=False)
        
        return map_data
    
    def update_map(self, map_id, map_data):
        """Update an existing map"""
        map_file = self.user_maps_dir / f"{map_id}.json"
        
        if not map_file.exists():
            raise FileNotFoundError(f"Map {map_id} not found")
        
        # Load existing map to preserve some metadata
        existing_data = self.get_map(map_id)
        map_data['id'] = map_id
        map_data['metadata'] = existing_data.get('metadata', {})
        map_data['metadata']['modified'] = datetime.now().isoformat()
        map_data['metadata']['author'] = self.username
        
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(map_data, f, indent=2, ensure_ascii=False)
        
        return map_data
    
    def get_map(self, map_id):
        """Get a map by ID"""
        map_file = self.user_maps_dir / f"{map_id}.json"
        
        if not map_file.exists():
            raise FileNotFoundError(f"Map {map_id} not found")
        
        with open(map_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def delete_map(self, map_id):
        """Delete a map"""
        map_file = self.user_maps_dir / f"{map_id}.json"
        
        if map_file.exists():
            map_file.unlink()
            return True
        return False
    
    def list_maps(self):
        """List all maps for this user"""
        maps = []
        
        if not self.user_maps_dir.exists():
            return maps
        
        for map_file in self.user_maps_dir.glob('*.json'):
            try:
                with open(map_file, 'r', encoding='utf-8') as f:
                    map_data = json.load(f)
                    map_data['id'] = map_file.stem
                    maps.append(map_data)
            except Exception as e:
                print(f"Error reading map file {map_file}: {e}")
        
        # Sort by modified date (most recent first)
        maps.sort(
            key=lambda m: m.get('metadata', {}).get('modified', ''),
            reverse=True
        )
        
        return maps
    
    @staticmethod
    def list_all_public_maps():
        """List all maps from all users (public)"""
        all_maps = []
        users_dir = Path(settings.USERS_DIR)
        
        if not users_dir.exists():
            return all_maps
        
        for user_dir in users_dir.iterdir():
            if user_dir.is_dir():
                maps_dir = user_dir / 'maps'
                if maps_dir.exists():
                    for map_file in maps_dir.glob('*.json'):
                        try:
                            with open(map_file, 'r', encoding='utf-8') as f:
                                map_data = json.load(f)
                                map_data['id'] = map_file.stem
                                all_maps.append(map_data)
                        except Exception as e:
                            print(f"Error reading map file {map_file}: {e}")
        
        # Sort by modified date (most recent first)
        all_maps.sort(
            key=lambda m: m.get('metadata', {}).get('modified', ''),
            reverse=True
        )
        
        return all_maps
