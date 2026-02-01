"""
Parser for Zombicide Mapeditor pack files (cfg format)
"""
import os
import re
from pathlib import Path
from django.conf import settings


def get_base_dir(pack_dir):
    """Get the base directory for relative paths"""
    pack_path = Path(pack_dir).resolve()
    assets_path = Path(settings.ASSETS_DIR).resolve()
    tiles_path = Path(settings.BG_MAPEDITOR_TILES_DIR).resolve()
    
    try:
        # Python 3.9+ has is_relative_to
        if hasattr(pack_path, 'is_relative_to'):
            if pack_path.is_relative_to(assets_path):
                return assets_path
            if pack_path.is_relative_to(tiles_path):
                return tiles_path
        else:
            # Fallback for older Python
            try:
                pack_path.relative_to(assets_path)
                return assets_path
            except ValueError:
                try:
                    pack_path.relative_to(tiles_path)
                    return tiles_path
                except ValueError:
                    pass
    except Exception:
        pass
    
    # Default to tiles for backward compatibility
    return tiles_path


class PackParser:
    """Parse Mapeditor pack structure and cfg files"""
    
    def __init__(self, pack_dir):
        self.pack_dir = Path(pack_dir)
        self.pack_id = self.pack_dir.name
        # Determine base directory for relative paths
        self.base_dir = get_base_dir(pack_dir)
        
    def parse_pack(self):
        """Parse a complete pack and return its structure"""
        pack_info = {
            'id': self.pack_id,
            'name': self.pack_id,
            'image': None,
            'align': 25,
            'categories': {}
        }
        
        # Parse root cfg
        root_cfg = self.pack_dir / 'cfg'
        if root_cfg.exists():
            root_data = self._parse_cfg_file(root_cfg)
            pack_info['name'] = root_data.get('name', self.pack_id)
            pack_info['image'] = root_data.get('image', 'guillotine.png')
            pack_info['align'] = int(root_data.get('align', 25))
        
        # Find and parse category directories
        for item in self.pack_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it's a category directory (starts with number followed by dot)
                # This matches: 01.tiles, 02.doors, 04.1.objectives, 05.1.survivors, 01B.vaults, etc.
                if re.match(r'^\d+[\.\d]', item.name):
                    category_name = item.name
                    category_data = self._parse_category(item, category_name)
                    if category_data:
                        pack_info['categories'][category_name] = category_data
        
        return pack_info
    
    def _parse_category(self, category_dir, category_name):
        """Parse a category directory (e.g., 01.tiles)"""
        category_cfg = category_dir / 'cfg'
        if not category_cfg.exists():
            return None
        
        cfg_data = self._parse_cfg_file(category_cfg)
        assets = self._scan_category_assets(category_dir, cfg_data)
        
        return {
            'name': cfg_data.get('name', category_name),
            'z_index': int(cfg_data.get('z-index', 0)),
            'align': int(cfg_data.get('align', 0)),
            'max': cfg_data.get('max', ''),
            'pairs': cfg_data.get('pairs', ''),
            'assets': assets
        }
    
    def _scan_category_assets(self, category_dir, cfg_data):
        """Scan category directory for assets"""
        assets = []
        max_dict = self._parse_max_string(cfg_data.get('max', ''))
        pairs_dict = self._parse_pairs_string(cfg_data.get('pairs', ''))
        
        # Scan for image files and directories
        for item in category_dir.iterdir():
            if item.is_file() and item.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                asset_name = item.name
                # Normalize path to use forward slashes for URLs
                rel_path = item.relative_to(self.base_dir)
                asset_path = str(rel_path).replace('\\', '/')
                
                # Check for rotations
                rotations = self._find_rotations(item)
                thumbnail = self._find_thumbnail(item)
                
                assets.append({
                    'name': asset_name,
                    'path': asset_path,
                    'thumbnail': thumbnail,
                    'rotations': rotations,
                    'max': max_dict.get(asset_name, None),
                    'pair': pairs_dict.get(asset_name, None)
                })
            elif item.is_dir() and not item.name.startswith('.'):
                # Asset with rotations in subdirectory (e.g., 10V.png/ contains r_0.png, r_thumb.png, etc.)
                asset_name = item.name
                main_image = item / 'r_0.png'
                if main_image.exists():
                    # Normalize path to use forward slashes for URLs
                    rel_path = main_image.relative_to(self.base_dir)
                    asset_path = str(rel_path).replace('\\', '/')
                    rotations = self._find_rotations_in_dir(item)
                    thumbnail = self._find_thumbnail_in_dir(item)
                    
                    assets.append({
                        'name': asset_name,
                        'path': asset_path,
                        'thumbnail': thumbnail,
                        'rotations': rotations,
                        'max': max_dict.get(asset_name, None),
                        'pair': pairs_dict.get(asset_name, None)
                    })
        
        return assets
    
    def _find_rotations(self, image_path):
        """Find rotation images for an asset"""
        rotations = {}
        base_path = image_path.parent / image_path.stem
        
        for angle in [0, 90, 180, 270]:
            rot_file = base_path / f'r_{angle}.png'
            if rot_file.exists():
                # Normalize path to use forward slashes for URLs
                rel_path = rot_file.relative_to(self.base_dir)
                rotations[angle] = str(rel_path).replace('\\', '/')
        
        return rotations
    
    def _find_rotations_in_dir(self, asset_dir):
        """Find rotation images in asset directory"""
        rotations = {}
        for angle in [0, 90, 180, 270]:
            rot_file = asset_dir / f'r_{angle}.png'
            if rot_file.exists():
                # Normalize path to use forward slashes for URLs
                rel_path = rot_file.relative_to(self.base_dir)
                rotations[angle] = str(rel_path).replace('\\', '/')
        return rotations
    
    def _find_thumbnail(self, image_path):
        """Find thumbnail for an asset"""
        base_path = image_path.parent / image_path.stem
        thumb_file = base_path / 'r_thumb.png'
        if thumb_file.exists():
            # Normalize path to use forward slashes for URLs
            rel_path = thumb_file.relative_to(self.base_dir)
            return str(rel_path).replace('\\', '/')
        
        # Check in subdirectory
        asset_dir = image_path.parent / image_path.stem
        if asset_dir.is_dir():
            thumb_file = asset_dir / 'r_thumb.png'
            if thumb_file.exists():
                # Normalize path to use forward slashes for URLs
                rel_path = thumb_file.relative_to(self.base_dir)
                return str(rel_path).replace('\\', '/')
        
        return None
    
    def _find_thumbnail(self, image_path):
        """Find thumbnail for an asset"""
        base_path = image_path.parent / image_path.stem
        thumb_file = base_path / 'r_thumb.png'
        if thumb_file.exists():
            # Normalize path to use forward slashes for URLs
            rel_path = thumb_file.relative_to(self.base_dir)
            return str(rel_path).replace('\\', '/')
        
        # Check in subdirectory
        asset_dir = image_path.parent / image_path.stem
        if asset_dir.is_dir():
            thumb_file = asset_dir / 'r_thumb.png'
            if thumb_file.exists():
                # Normalize path to use forward slashes for URLs
                rel_path = thumb_file.relative_to(self.base_dir)
                return str(rel_path).replace('\\', '/')
        
        return None
    
    def _find_thumbnail_in_dir(self, asset_dir):
        """Find thumbnail in asset directory"""
        thumb_file = asset_dir / 'r_thumb.png'
        if thumb_file.exists():
            # Normalize path to use forward slashes for URLs
            rel_path = thumb_file.relative_to(self.base_dir)
            return str(rel_path).replace('\\', '/')
        return None
    
    def _parse_cfg_file(self, cfg_path):
        """Parse a cfg file and return a dict"""
        data = {}
        try:
            with open(cfg_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        data[key.strip()] = value.strip()
        except Exception as e:
            print(f"Error parsing cfg file {cfg_path}: {e}")
        return data
    
    def _parse_max_string(self, max_str):
        """Parse max string like 'file.png:1;file2.png:2'"""
        max_dict = {}
        if not max_str:
            return max_dict
        
        for item in max_str.split(';'):
            if ':' in item:
                filename, count = item.split(':', 1)
                try:
                    max_dict[filename] = int(count)
                except ValueError:
                    max_dict[filename] = None
            else:
                max_dict[item] = None
        
        return max_dict
    
    def _parse_pairs_string(self, pairs_str):
        """Parse pairs string like 'file1.png:file2.png;file3.png:file4.png'"""
        pairs_dict = {}
        if not pairs_str:
            return pairs_dict
        
        for pair in pairs_str.split(';'):
            if ':' in pair:
                file1, file2 = pair.split(':', 1)
                pairs_dict[file1] = file2
                pairs_dict[file2] = file1
        
        return pairs_dict


class AssetIndexer:
    """Index all packs in bgmapeditor_tiles directory"""
    
    @staticmethod
    def index_all_packs():
        """Index all packs in the bgmapeditor_tiles directory"""
        packs = []
        tiles_dir = Path(settings.BG_MAPEDITOR_TILES_DIR)
        
        if not tiles_dir.exists():
            return packs
        
        for item in tiles_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it looks like a pack directory
                if item.name.startswith('G-Zombicide-') or (item / 'cfg').exists():
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
