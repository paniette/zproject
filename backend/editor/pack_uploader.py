"""
Upload and normalize custom pack assets
"""
import re
import shutil
from pathlib import Path
from PIL import Image
from django.conf import settings
from .utils import ensure_directory


def sanitize_asset_name(name):
    """Safe folder name under pack/category (no path traversal)."""
    if not name or not str(name).strip():
        raise ValueError('asset_name is required')
    s = str(name).strip()
    if '..' in s or '/' in s or '\\' in s:
        raise ValueError('invalid characters in asset_name')
    if s in ('.', '..') or s.startswith('.'):
        raise ValueError('invalid asset_name')
    s = re.sub(r'[\x00-\x1f<>:"|?*]', '_', s)
    return s


def sanitize_path_segment(seg, field_name):
    """Valide un segment de chemin (pack, catégorie) contre traversal et caractères dangereux."""
    if not seg or not str(seg).strip():
        raise ValueError(f'{field_name} is required')
    s = str(seg).strip()
    if '..' in s or '/' in s or '\\' in s:
        raise ValueError(f'invalid {field_name}')
    return s


class PackUploader:
    """Handle upload and normalization of custom pack assets"""
    
    def __init__(self, pack_name):
        """pack_name : id dossier pack sous ASSETS_DIR (créé si besoin)."""
        self.pack_name = sanitize_path_segment(pack_name, 'pack_name')
        # Create packs in /assets/ directory (unified location)
        self.pack_dir = Path(settings.ASSETS_DIR) / self.pack_name
        ensure_directory(self.pack_dir)
    
    def upload_and_normalize(
        self,
        image_file,
        asset_name,
        category,
        target_size=None,
        target_width=None,
        target_height=None,
    ):
        """Upload an image and normalize it (create rotations and thumbnail).

        Either pass target_size (square) or target_width + target_height (rectangle).
        """
        asset_name = sanitize_asset_name(asset_name)
        category = sanitize_path_segment(category, 'category')

        if target_width is not None and target_height is not None:
            tw, th = int(target_width), int(target_height)
        elif target_size is not None:
            ts = int(target_size)
            tw, th = ts, ts
        else:
            tw, th = 32, 32

        if tw < 8 or th < 8 or tw > 2048 or th > 2048:
            raise ValueError('target dimensions must be between 8 and 2048')

        # Ensure category directory exists
        category_dir = self.pack_dir / category
        ensure_directory(category_dir)

        # Create asset directory
        asset_dir = category_dir / asset_name
        ensure_directory(asset_dir)

        # Load and resize image
        img = Image.open(image_file)
        img = img.convert('RGBA')
        img_resized = img.resize((tw, th), Image.Resampling.LANCZOS)
        is_square = tw == th

        rotations = {}
        r0_path = asset_dir / 'r_0.png'
        img_resized.save(r0_path, 'PNG')
        try:
            rotations[0] = str(r0_path.relative_to(settings.ASSETS_DIR))
        except ValueError:
            try:
                rotations[0] = str(r0_path.relative_to(settings.BG_MAPEDITOR_TILES_DIR))
            except ValueError:
                rotations[0] = str(r0_path.relative_to(settings.PACKS_DIR))

        for angle in [90, 180, 270]:
            rot_path = asset_dir / f'r_{angle}.png'
            if is_square:
                rotated = img_resized.rotate(-angle, expand=False)
                rotated.save(rot_path, 'PNG')
            else:
                shutil.copyfile(r0_path, rot_path)
            try:
                rotations[angle] = str(rot_path.relative_to(settings.ASSETS_DIR))
            except ValueError:
                try:
                    rotations[angle] = str(rot_path.relative_to(settings.BG_MAPEDITOR_TILES_DIR))
                except ValueError:
                    rotations[angle] = str(rot_path.relative_to(settings.PACKS_DIR))

        # Thumbnail: fit inside ~64px box, keep aspect ratio
        thumb_max = 64
        scale = min(thumb_max / tw, thumb_max / th, 1.0)
        t_w = max(1, int(round(tw * scale)))
        t_h = max(1, int(round(th * scale)))
        thumb = img_resized.resize((t_w, t_h), Image.Resampling.LANCZOS)
        thumb_path = asset_dir / 'r_thumb.png'
        thumb.save(thumb_path, 'PNG')
        
        # Update cfg file
        self._update_category_cfg(category, asset_name)
        
        # Get relative paths (prefer assets directory)
        main_path = asset_dir / 'r_0.png'
        try:
            main_path_rel = str(main_path.relative_to(settings.ASSETS_DIR))
        except ValueError:
            try:
                main_path_rel = str(main_path.relative_to(settings.BG_MAPEDITOR_TILES_DIR))
            except ValueError:
                main_path_rel = str(main_path.relative_to(settings.PACKS_DIR))
        
        try:
            thumb_path_rel = str(thumb_path.relative_to(settings.ASSETS_DIR))
        except ValueError:
            try:
                thumb_path_rel = str(thumb_path.relative_to(settings.BG_MAPEDITOR_TILES_DIR))
            except ValueError:
                thumb_path_rel = str(thumb_path.relative_to(settings.PACKS_DIR))
        
        return {
            'name': asset_name,
            'path': main_path_rel,
            'thumbnail': thumb_path_rel,
            'rotations': rotations
        }
    
    def _update_category_cfg(self, category, asset_name):
        """Update or create cfg file for category"""
        category_dir = self.pack_dir / category
        cfg_file = category_dir / 'cfg'
        
        # Read existing cfg or create new
        cfg_data = {}
        if cfg_file.exists():
            with open(cfg_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        cfg_data[key.strip()] = value.strip()
        
        # Update max field
        max_str = cfg_data.get('max', '')
        if max_str:
            max_str += f';{asset_name}.png'
        else:
            max_str = f'{asset_name}.png'
        cfg_data['max'] = max_str
        
        # Write cfg file
        with open(cfg_file, 'w', encoding='utf-8') as f:
            f.write(f"name={cfg_data.get('name', category)}\n")
            if 'z-index' in cfg_data:
                f.write(f"z-index={cfg_data['z-index']}\n")
            if 'align' in cfg_data:
                f.write(f"align={cfg_data['align']}\n")
            f.write(f"max={cfg_data['max']}\n")
            if 'pairs' in cfg_data:
                f.write(f"pairs={cfg_data['pairs']}\n")
        
        # Update pack root cfg if needed
        self._update_pack_cfg()
    
    def _update_pack_cfg(self):
        """Update or create pack root cfg file"""
        cfg_file = self.pack_dir / 'cfg'
        
        if not cfg_file.exists():
            with open(cfg_file, 'w', encoding='utf-8') as f:
                f.write(f"name={self.pack_name}\n")
                f.write("image=guillotine.png\n")
                f.write("align=25\n")
    
    @staticmethod
    def create_pack(pack_name):
        """Create a new custom pack in /assets/ directory"""
        pack_name = sanitize_path_segment(pack_name, 'pack_name')
        pack_dir = Path(settings.ASSETS_DIR) / pack_name
        ensure_directory(pack_dir)
        
        # Create root cfg
        cfg_file = pack_dir / 'cfg'
        with open(cfg_file, 'w', encoding='utf-8') as f:
            f.write(f"name={pack_name}\n")
            f.write("image=guillotine.png\n")
            f.write("align=25\n")
        
        return pack_dir
