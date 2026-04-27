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

def infer_game_type(pack_id: str) -> str:
    """
    Infère le type de jeu (Modern/Fantasy/Western/Sci‑Fi/Classic/Night) depuis l'id du pack.
    Source des catégories : https://www.zombicide.com/fr/mapeditor-zombicide/
    """
    pid = (pack_id or "").upper()

    # Modern (2nd edition + extensions)
    if pid.endswith("-A5-2E") or pid.endswith("-A6-ZC") or pid.endswith("-A7-FH"):
        return "modern"

    # Sci‑Fi (Invader)
    if pid.startswith("G-ZOMBICIDE-IV"):
        return "scifi"

    # Night Of The Living Dead
    # Le pack présent dans ce repo est `G-Zombicide-D1-LD` (Living Dead) : ne pas le classer en Western.
    if pid.startswith("E1_") or "NIGHT" in pid or pid.endswith("-LD") or "-LD" in pid or "LIVING" in pid:
        return "night"

    # Western (Undead or Alive)
    if pid.startswith("G-ZOMBICIDE-D1") or pid.startswith("D1_") or "UNDEAD" in pid:
        return "western"

    # Fantasy (BP/WD/EE/TMNT, etc.)
    if pid.startswith("G-ZOMBICIDE-BP") or pid.startswith("G-ZOMBICIDE-WD") or pid.startswith("G-ZOMBICIDE-EE") or pid.startswith("G-ZOMBICIDE-TMNT"):
        return "fantasy"

    # Zombicide (Classic) : extensions/classiques
    if pid.startswith("G-ZOMBICIDE-PO") or pid.startswith("G-ZOMBICIDE-RM") or pid.startswith("G-ZOMBICIDE-TCM") or pid.startswith("G-ZOMBICIDE-AN"):
        return "classic"
    # Base classique (G-Zombicide) + autres packs non matchés ci-dessus
    if pid == "G-ZOMBICIDE":
        return "classic"

    # Fallback raisonnable
    # Si ça commence par G-Zombicide mais n'a matché aucun mode dédié, c'est très probablement Classic.
    if pid.startswith("G-ZOMBICIDE"):
        return "classic"
    return "fantasy"

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
            "gameType": infer_game_type(pack['id']),
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
