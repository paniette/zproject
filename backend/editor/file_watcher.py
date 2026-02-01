"""
File watcher for detecting changes in bgmapeditor_tiles directory
"""
import os
from pathlib import Path
from django.conf import settings
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class PackChangeHandler(FileSystemEventHandler):
    """Handle file system events for pack changes"""
    
    def __init__(self, callback=None):
        self.callback = callback
        super().__init__()
    
    def on_created(self, event):
        if not event.is_directory:
            self._notify_change(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self._notify_change(event.src_path)
    
    def on_moved(self, event):
        self._notify_change(event.dest_path)
    
    def on_deleted(self, event):
        self._notify_change(event.src_path)
    
    def _notify_change(self, path):
        """Notify about a change in the packs directory"""
        if self.callback:
            try:
                self.callback(path)
            except Exception as e:
                print(f"Error in change callback: {e}")


class PackFileWatcher:
    """Watch for changes in bgmapeditor_tiles directory"""
    
    def __init__(self):
        self.observer = None
        self.watching = False
        self.callbacks = []
    
    def start(self, callback=None):
        """Start watching the directory"""
        if self.watching:
            return
        
        # Watch assets directory (unified location)
        assets_dir = Path(settings.ASSETS_DIR)
        if not assets_dir.exists():
            os.makedirs(assets_dir, exist_ok=True)
        
        if callback:
            self.callbacks.append(callback)
        
        event_handler = PackChangeHandler(self._handle_change)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(assets_dir), recursive=True)
        self.observer.start()
        self.watching = True
        print(f"Started watching {assets_dir}")
    
    def stop(self):
        """Stop watching"""
        if self.observer and self.watching:
            self.observer.stop()
            self.observer.join()
            self.watching = False
            print("Stopped watching")
    
    def _handle_change(self, path):
        """Handle a file system change"""
        for callback in self.callbacks:
            try:
                callback(path)
            except Exception as e:
                print(f"Error in change callback: {e}")
    
    def add_callback(self, callback):
        """Add a callback function to be called on changes"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)


# Global watcher instance
_watcher = None

def get_watcher():
    """Get or create the global file watcher instance"""
    global _watcher
    if _watcher is None:
        _watcher = PackFileWatcher()
    return _watcher
