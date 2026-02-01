"""
Script to generate a static packs index JSON file
This allows the frontend to work without Django backend
"""
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from django.conf import settings
from django.conf import settings as django_settings
import os

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zombicide_editor.settings')

# Import Django
import django
django.setup()

from api.parsers.asset_indexer import AssetIndexer
from api.parsers.pack_parser import PackParser

def generate_packs_index():
    """Generate a static JSON file with all packs and their assets"""
    
    print("Indexing packs...")
    packs = AssetIndexer.index_all_packs()
    
    print(f"Found {len(packs)} packs")
    
    # Build the index structure
    index = {
        "packs": [],
        "generated_at": None
    }
    
    from datetime import datetime
    index["generated_at"] = datetime.now().isoformat()
    
    for pack in packs:
        print(f"Processing pack: {pack['id']}")
        
        # Get assets for this pack
        try:
            assets = AssetIndexer.get_pack_assets(pack['id'])
        except Exception as e:
            print(f"Error getting assets for {pack['id']}: {e}")
            assets = {}
        
        pack_data = {
            "id": pack['id'],
            "name": pack.get('name', pack['id']),
            "image": pack.get('image'),
            "align": pack.get('align', 25),
            "assets": assets
        }
        
        index["packs"].append(pack_data)
    
    # Write to frontend public directory
    output_path = Path(__file__).parent.parent / 'frontend' / 'public' / 'packs-index.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"Index generated successfully: {output_path}")
    print(f"Total packs: {len(index['packs'])}")
    
    return output_path

if __name__ == '__main__':
    try:
        generate_packs_index()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
