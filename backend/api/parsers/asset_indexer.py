"""
Asset indexer - wrapper for pack parsing
"""
from .pack_parser import PackParser
from pathlib import Path
from django.conf import settings

class AssetIndexer:
    """Index all packs in assets directory"""
    
    @staticmethod
    def index_all_packs():
        """Index all packs in the assets directory (and legacy bgmapeditor_tiles)"""
        packs = []
        
        # Check assets directory first (new location)
        assets_dir = Path(settings.ASSETS_DIR)
        if assets_dir.exists():
            for item in assets_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Vérifier que le dossier existe vraiment
                    if not item.exists():
                        continue
                    if item.name.startswith('G-Zombicide-') or (item / 'cfg').exists():
                        try:
                            parser = PackParser(item)
                            pack_info = parser.parse_pack()
                            packs.append(pack_info)
                        except Exception as e:
                            print(f"Error indexing pack {item.name}: {e}")
        
        # Also check legacy bgmapeditor_tiles directory
        tiles_dir = Path(settings.BG_MAPEDITOR_TILES_DIR)
        if tiles_dir.exists():
            for item in tiles_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Vérifier que le dossier existe vraiment
                    if not item.exists():
                        continue
                    # Check if it looks like a pack directory
                    if item.name.startswith('G-Zombicide-') or (item / 'cfg').exists():
                        # Skip if already found in assets
                        if not any(p['id'] == item.name for p in packs):
                            try:
                                parser = PackParser(item)
                                pack_info = parser.parse_pack()
                                packs.append(pack_info)
                            except Exception as e:
                                print(f"Error indexing pack {item.name}: {e}")
        
        return packs
    
    @staticmethod
    def get_pack_assets(pack_id):
        """Get assets for a specific pack"""
        # Try assets directory first
        assets_dir = Path(settings.ASSETS_DIR)
        pack_dir = assets_dir / pack_id
        
        if not pack_dir.exists():
            # Try legacy directory
            tiles_dir = Path(settings.BG_MAPEDITOR_TILES_DIR)
            pack_dir = tiles_dir / pack_id
        
        if not pack_dir.exists():
            return {}
        
        parser = PackParser(pack_dir)
        pack_info = parser.parse_pack()
        
        # Return assets organized by category
        assets_by_category = {}
        for category_name, category_data in pack_info['categories'].items():
            assets_by_category[category_name] = category_data['assets']
        
        return assets_by_category
