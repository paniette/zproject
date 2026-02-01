"""
Upload and extract ZIP packs
"""
import os
import zipfile
import shutil
from pathlib import Path
from django.conf import settings
from .utils import ensure_directory
from api.parsers.pack_parser import PackParser


class PackZipUploader:
    """Handle upload and extraction of ZIP packs"""
    
    MAX_ZIP_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.cfg', '.txt', '.licence', '.license'}
    
    @staticmethod
    def upload_and_extract(zip_file, destination='assets', replace_existing=False):
        """Upload and extract a ZIP pack"""
        # Validate file size
        zip_file.seek(0, os.SEEK_END)
        file_size = zip_file.tell()
        zip_file.seek(0)
        
        if file_size > PackZipUploader.MAX_ZIP_SIZE:
            raise ValueError(f"ZIP file too large (max {PackZipUploader.MAX_ZIP_SIZE / 1024 / 1024}MB)")
        
        # Always extract to assets directory (unified location)
        dest_dir = Path(settings.ASSETS_DIR)
        ensure_directory(dest_dir)
        
        # Extract ZIP to temporary location first
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract ZIP
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Validate contents
                for member in zip_ref.namelist():
                    if member.startswith('/') or '..' in member:
                        raise ValueError("Invalid ZIP structure: unsafe paths")
                    
                    # Check file extension
                    member_path = Path(member)
                    if member_path.suffix.lower() not in PackZipUploader.ALLOWED_EXTENSIONS and not member_path.is_dir():
                        # Allow directories
                        continue
                
                zip_ref.extractall(temp_path)
            
            # Find pack directory (should be at root or one level deep)
            pack_dir = None
            for item in temp_path.iterdir():
                if item.is_dir():
                    # Check if it looks like a pack (has cfg file)
                    if (item / 'cfg').exists():
                        pack_dir = item
                        break
                    # Or check subdirectories
                    for subitem in item.iterdir():
                        if subitem.is_dir() and (subitem / 'cfg').exists():
                            pack_dir = subitem
                            break
                    if pack_dir:
                        break
            
            if not pack_dir:
                raise ValueError("No valid pack structure found in ZIP (missing cfg file)")
            
            pack_name = pack_dir.name
            final_pack_dir = dest_dir / pack_name
            
            # Handle existing pack
            if final_pack_dir.exists():
                if replace_existing:
                    shutil.rmtree(final_pack_dir)
                else:
                    # Rename with suffix
                    counter = 1
                    while (dest_dir / f"{pack_name}_{counter}").exists():
                        counter += 1
                    pack_name = f"{pack_name}_{counter}"
                    final_pack_dir = dest_dir / pack_name
            
            # Move pack to final location
            shutil.move(str(pack_dir), str(final_pack_dir))
            
            # Validate pack structure
            try:
                parser = PackParser(final_pack_dir)
                pack_info = parser.parse_pack()
            except Exception as e:
                # Clean up on validation failure
                if final_pack_dir.exists():
                    shutil.rmtree(final_pack_dir)
                raise ValueError(f"Invalid pack structure: {str(e)}")
            
            return {
                'id': pack_name,
                'name': pack_info['name'],
                'path': str(final_pack_dir.relative_to(settings.ASSETS_DIR)),
                'categories': list(pack_info['categories'].keys())
            }
    
    @staticmethod
    def list_uploaded_packs():
        """List all uploaded packs in assets directory"""
        assets_dir = Path(settings.ASSETS_DIR)
        
        if not assets_dir.exists():
            return []
        
        packs = []
        for pack_dir in assets_dir.iterdir():
            if pack_dir.is_dir() and not pack_dir.name.startswith('.'):
                try:
                    parser = PackParser(pack_dir)
                    pack_info = parser.parse_pack()
                    packs.append({
                        'id': pack_info['id'],
                        'name': pack_info['name'],
                        'image': pack_info.get('image')
                    })
                except Exception as e:
                    print(f"Error parsing uploaded pack {pack_dir.name}: {e}")
        
        return packs
    
    @staticmethod
    def delete_uploaded_pack(pack_id):
        """Delete an uploaded pack from assets directory"""
        assets_dir = Path(settings.ASSETS_DIR)
        pack_dir = assets_dir / pack_id
        
        if pack_dir.exists() and pack_dir.is_dir():
            shutil.rmtree(pack_dir)
            return True
        return False
