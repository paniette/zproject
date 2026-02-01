"""
User manager for temporary users
"""
import os
from pathlib import Path
from django.conf import settings
from .utils import ensure_directory


class UserManager:
    """Manage temporary users"""
    
    DEFAULT_USER = 'temp'
    
    @staticmethod
    def ensure_user(username):
        """Ensure a user directory exists"""
        user_dir = Path(settings.USERS_DIR) / username
        maps_dir = user_dir / 'maps'
        ensure_directory(maps_dir)
        return user_dir
    
    @staticmethod
    def list_users():
        """List all available users"""
        users_dir = Path(settings.USERS_DIR)
        
        if not users_dir.exists():
            return [UserManager.DEFAULT_USER]
        
        users = []
        for item in users_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                users.append(item.name)
        
        # Ensure default user exists
        if UserManager.DEFAULT_USER not in users:
            UserManager.ensure_user(UserManager.DEFAULT_USER)
            users.append(UserManager.DEFAULT_USER)
        
        return sorted(users)
    
    @staticmethod
    def create_user(username):
        """Create a new user directory"""
        if not username or username.strip() == '':
            raise ValueError("Username cannot be empty")
        
        user_dir = UserManager.ensure_user(username)
        return user_dir
    
    @staticmethod
    def user_exists(username):
        """Check if a user exists"""
        user_dir = Path(settings.USERS_DIR) / username
        return user_dir.exists() and user_dir.is_dir()
