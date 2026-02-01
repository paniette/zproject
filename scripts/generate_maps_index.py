"""
Script to generate a static maps index JSON file
This allows the frontend to work without Django backend
"""
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from django.conf import settings
import os

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zombicide_editor.settings')

# Import Django
import django
django.setup()

from editor.map_manager import MapManager


def generate_maps_index():
    """Generate a static JSON file with all maps from all users"""
    
    print("Indexing maps...")
    
    # Get all maps from all users
    all_maps = MapManager.list_all_public_maps()
    
    print(f"Found {len(all_maps)} maps")
    
    # Build the index structure
    index = {
        "maps": [],
        "generated_at": None
    }
    
    from datetime import datetime
    index["generated_at"] = datetime.now().isoformat()
    
    for map_data in all_maps:
        # Extract only necessary metadata for the index
        map_entry = {
            "id": map_data.get('id'),
            "name": map_data.get('name', 'Untitled'),
            "metadata": map_data.get('metadata', {})
        }
        index["maps"].append(map_entry)
    
    # Write to frontend public directory
    output_path = Path(__file__).parent.parent / 'frontend' / 'public' / 'maps-index.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"Index generated successfully: {output_path}")
    print(f"Total maps: {len(index['maps'])}")
    
    # Also copy individual map files to public directory for static access
    maps_public_dir = Path(__file__).parent.parent / 'frontend' / 'public' / 'maps'
    maps_public_dir.mkdir(parents=True, exist_ok=True)
    
    print("\nCopying map files to public directory...")
    users_dir = Path(settings.USERS_DIR)
    copied_count = 0
    
    if users_dir.exists():
        for user_dir in users_dir.iterdir():
            if user_dir.is_dir():
                maps_dir = user_dir / 'maps'
                if maps_dir.exists():
                    for map_file in maps_dir.glob('*.json'):
                        try:
                            # Copy map file to public/maps/
                            import shutil
                            dest_file = maps_public_dir / map_file.name
                            shutil.copy2(map_file, dest_file)
                            copied_count += 1
                        except Exception as e:
                            print(f"Error copying map file {map_file}: {e}")
    
    print(f"Copied {copied_count} map files to {maps_public_dir}")
    
    return output_path


if __name__ == '__main__':
    try:
        generate_maps_index()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
