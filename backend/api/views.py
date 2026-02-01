from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
from .parsers.asset_indexer import AssetIndexer
from .serializers import PackSerializer

class PackListView(APIView):
    def get(self, request):
        """List all available packs"""
        try:
            # Always re-index to catch changes (file watcher will trigger this)
            packs = AssetIndexer.index_all_packs()
            # Serialize packs
            pack_data = []
            for pack in packs:
                # Check if pack directory still exists
                from pathlib import Path
                from django.conf import settings
                pack_dir_assets = Path(settings.ASSETS_DIR) / pack['id']
                pack_dir_tiles = Path(settings.BG_MAPEDITOR_TILES_DIR) / pack['id']
                if not pack_dir_assets.exists() and not pack_dir_tiles.exists():
                    continue  # Skip deleted packs
                
                pack_data.append({
                    'id': pack['id'],
                    'name': pack['name'],
                    'image': pack.get('image'),
                    'align': pack.get('align', 25)
                })
            return Response(pack_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PackDetailView(APIView):
    def get(self, request, pack_id):
        """Get details of a specific pack"""
        try:
            packs = AssetIndexer.index_all_packs()
            pack = next((p for p in packs if p['id'] == pack_id), None)
            
            if not pack:
                return Response(
                    {"error": "Pack not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                'id': pack['id'],
                'name': pack['name'],
                'image': pack.get('image'),
                'align': pack.get('align', 25),
                'categories': list(pack['categories'].keys())
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PackAssetsView(APIView):
    def get(self, request, pack_id):
        """Get assets for a specific pack, organized by category"""
        try:
            assets_by_category = AssetIndexer.get_pack_assets(pack_id)
            if not assets_by_category:
                return Response(
                    {"error": "Pack not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Format assets for frontend
            formatted_assets = {}
            for category_name, assets in assets_by_category.items():
                formatted_assets[category_name] = [
                    {
                        'name': asset['name'],
                        'path': asset['path'],
                        'thumbnail': asset.get('thumbnail'),
                        'rotations': asset.get('rotations', {}),
                        'max': asset.get('max'),
                        'pair': asset.get('pair'),
                        'category': category_name
                    }
                    for asset in assets
                ]
            
            return Response(formatted_assets, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AssetView(APIView):
    def get(self, request, asset_path):
        # Handle paths that already include directory name
        if asset_path.startswith('assets/'):
            asset_path = asset_path[7:]  # Remove 'assets/' prefix
            full_path = os.path.join(settings.ASSETS_DIR, asset_path)
        elif asset_path.startswith('bgmapeditor_tiles/'):
            asset_path = asset_path[18:]  # Remove 'bgmapeditor_tiles/' prefix
            full_path = os.path.join(settings.BG_MAPEDITOR_TILES_DIR, asset_path)
        else:
            # Try both directories - assets first, then bgmapeditor_tiles
            full_path = os.path.join(settings.ASSETS_DIR, asset_path)
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                # Try legacy bgmapeditor_tiles directory
                full_path = os.path.join(settings.BG_MAPEDITOR_TILES_DIR, asset_path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            return FileResponse(open(full_path, 'rb'), content_type='image/png')
        raise Http404(f"Asset not found: {asset_path}")

class UserListView(APIView):
    def get(self, request):
        """List all temporary users"""
        try:
            from editor.user_manager import UserManager
            users = UserManager.list_users()
            return Response({"users": users}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new temporary user"""
        try:
            from editor.user_manager import UserManager
            username = request.data.get('username')
            if not username:
                return Response(
                    {"error": "Username is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            UserManager.create_user(username)
            return Response(
                {"message": f"User {username} created"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserMapsView(APIView):
    def get(self, request, username):
        """List all maps for a user"""
        try:
            from editor.map_manager import MapManager
            manager = MapManager(username)
            maps = manager.list_maps()
            return Response({"maps": maps}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request, username):
        """Create a new map for a user"""
        try:
            from editor.map_manager import MapManager
            from editor.user_manager import UserManager
            
            # Ensure user exists
            UserManager.ensure_user(username)
            
            manager = MapManager(username)
            map_data = request.data
            created_map = manager.create_map(map_data)
            return Response(created_map, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MapDetailView(APIView):
    def get(self, request, username, map_id):
        """Get a specific map"""
        try:
            from editor.map_manager import MapManager
            manager = MapManager(username)
            map_data = manager.get_map(map_id)
            return Response(map_data, status=status.HTTP_200_OK)
        except FileNotFoundError:
            return Response(
                {"error": "Map not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, username, map_id):
        """Update a map"""
        try:
            from editor.map_manager import MapManager
            manager = MapManager(username)
            map_data = request.data
            updated_map = manager.update_map(map_id, map_data)
            return Response(updated_map, status=status.HTTP_200_OK)
        except FileNotFoundError:
            return Response(
                {"error": "Map not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, username, map_id):
        """Delete a map"""
        try:
            from editor.map_manager import MapManager
            manager = MapManager(username)
            manager.delete_map(map_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PublicMapsView(APIView):
    def get(self, request):
        """List all public maps (from all users)"""
        try:
            from editor.map_manager import MapManager
            maps = MapManager.list_all_public_maps()
            return Response({"maps": maps}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(csrf_exempt, name='dispatch')
class CustomPackUploadView(APIView):
    def post(self, request):
        """Upload and normalize a custom asset"""
        try:
            from editor.pack_uploader import PackUploader
            
            image_file = request.FILES.get('image')
            asset_name = request.data.get('asset_name')
            target_size = int(request.data.get('target_size', 32))
            category = request.data.get('category', '01.tiles')
            pack_name = request.data.get('pack_name', 'custom')
            
            if not image_file or not asset_name:
                return Response(
                    {"error": "image and asset_name are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploader = PackUploader(pack_name)
            result = uploader.upload_and_normalize(image_file, asset_name, target_size, category)
            
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CustomPackListView(APIView):
    def get(self, request):
        """List custom packs"""
        try:
            from api.parsers.asset_indexer import AssetIndexer
            from pathlib import Path
            from django.conf import settings
            
            custom_packs_dir = Path(settings.PACKS_DIR) / 'custom'
            packs = []
            
            if custom_packs_dir.exists():
                for pack_dir in custom_packs_dir.iterdir():
                    if pack_dir.is_dir() and not pack_dir.name.startswith('.'):
                        try:
                            from api.parsers.pack_parser import PackParser
                            parser = PackParser(pack_dir)
                            pack_info = parser.parse_pack()
                            packs.append({
                                'id': pack_info['id'],
                                'name': pack_info['name'],
                                'image': pack_info.get('image')
                            })
                        except Exception as e:
                            print(f"Error parsing custom pack {pack_dir.name}: {e}")
            
            return Response(packs, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(csrf_exempt, name='dispatch')
class PackZipUploadView(APIView):
    def post(self, request):
        """Upload and extract a ZIP pack"""
        try:
            from editor.pack_zip_uploader import PackZipUploader
            
            zip_file = request.FILES.get('zip_file')
            destination = request.data.get('destination', 'uploaded')
            replace_existing = request.data.get('replace_existing', False)
            
            if not zip_file:
                return Response(
                    {"error": "zip_file is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = PackZipUploader.upload_and_extract(zip_file, destination, replace_existing)
            
            return Response(result, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UploadedPackListView(APIView):
    def get(self, request):
        """List uploaded packs"""
        try:
            from editor.pack_zip_uploader import PackZipUploader
            packs = PackZipUploader.list_uploaded_packs()
            return Response(packs, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UploadedPackDeleteView(APIView):
    def delete(self, request, pack_id):
        """Delete an uploaded pack from assets directory"""
        try:
            from editor.pack_zip_uploader import PackZipUploader
            from pathlib import Path
            from django.conf import settings
            
            # Try to delete from assets directory
            assets_dir = Path(settings.ASSETS_DIR)
            pack_dir = assets_dir / pack_id
            
            if pack_dir.exists() and pack_dir.is_dir():
                import shutil
                shutil.rmtree(pack_dir)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"error": "Pack not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
