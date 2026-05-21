"""Routes /api/packs/* et uploads (ordre des routes = même contrainte que l'ancien urls.py Django)."""
from __future__ import annotations

import shutil
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from starlette.responses import Response

import app_config
from api.parsers.asset_indexer import AssetIndexer
from api.parsers.pack_parser import PackParser
from editor.pack_meta import write_pack_game_type
from editor.pack_uploader import PackUploader
from editor.pack_zip_uploader import PackZipUploader

from .packs_helpers import get_pack_game_type, parse_form_bool

router = APIRouter(tags=["packs"])


@router.get("/packs/")
def list_packs():
    try:
        packs = AssetIndexer.index_all_packs()
        pack_data = []
        for pack in packs:
            pack_dir_assets = Path(app_config.ASSETS_DIR) / pack["id"]
            pack_dir_tiles = Path(app_config.BG_MAPEDITOR_TILES_DIR) / pack["id"]
            if not pack_dir_assets.exists() and not pack_dir_tiles.exists():
                continue
            pack_data.append(
                {
                    "id": pack["id"],
                    "name": pack["name"],
                    "image": pack.get("image"),
                    "align": pack.get("align", 25),
                    "gameType": get_pack_game_type(pack),
                }
            )
        return pack_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/packs/custom/upload/")
async def custom_pack_upload(
    image: UploadFile = File(...),
    asset_name: str = Form(...),
    category: str = Form("01.tiles"),
    pack_name: str = Form("custom"),
    target_width: str | None = Form(None),
    target_height: str | None = Form(None),
    target_size: str = Form("32"),
    game_type: str | None = Form(None),
):
    try:
        if not asset_name:
            raise HTTPException(status_code=400, detail="image and asset_name are required")

        raw = await image.read()
        image_file = BytesIO(raw)

        uploader = PackUploader(pack_name)
        tw = target_width
        th = target_height
        if tw is not None and th is not None and str(tw).strip() != "" and str(th).strip() != "":
            result = uploader.upload_and_normalize(
                image_file,
                asset_name,
                category,
                target_width=int(tw),
                target_height=int(th),
            )
        else:
            result = uploader.upload_and_normalize(
                image_file,
                asset_name,
                category,
                target_size=int(target_size or 32),
            )

        if game_type:
            write_pack_game_type(pack_name, game_type)

        return JSONResponse(content=result, status_code=201)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/packs/custom/")
def list_custom_packs():
    try:
        custom_packs_dir = Path(app_config.PACKS_DIR) / "custom"
        packs = []
        if custom_packs_dir.exists():
            for pack_dir in custom_packs_dir.iterdir():
                if pack_dir.is_dir() and not pack_dir.name.startswith("."):
                    try:
                        parser = PackParser(pack_dir)
                        pack_info = parser.parse_pack()
                        packs.append(
                            {
                                "id": pack_info["id"],
                                "name": pack_info["name"],
                                "image": pack_info.get("image"),
                            }
                        )
                    except Exception as e:
                        print(f"Error parsing custom pack {pack_dir.name}: {e}")
        return packs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/packs/upload-zip/")
async def pack_zip_upload(
    zip_file: UploadFile = File(...),
    destination: str = Form("uploaded"),
    replace_existing: str = Form("false"),
    game_type: str | None = Form(None),
):
    try:
        raw = await zip_file.read()
        bio = BytesIO(raw)
        replace_flag = parse_form_bool(replace_existing)
        result = PackZipUploader.upload_and_extract(
            bio, destination, replace_flag, game_type=game_type
        )
        return JSONResponse(content=result, status_code=201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/packs/uploaded/")
def list_uploaded_packs():
    try:
        return PackZipUploader.list_uploaded_packs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/packs/uploaded/{pack_id}/")
def delete_uploaded_pack(pack_id: str):
    try:
        assets_dir = Path(app_config.ASSETS_DIR)
        pack_dir = assets_dir / pack_id
        if pack_dir.exists() and pack_dir.is_dir():
            shutil.rmtree(pack_dir)
            return Response(status_code=204)
        raise HTTPException(status_code=404, detail="Pack not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/packs/{pack_id}/assets/")
def pack_assets(pack_id: str):
    try:
        assets_by_category = AssetIndexer.get_pack_assets(pack_id)
        if not assets_by_category:
            raise HTTPException(status_code=404, detail="Pack not found")
        formatted_assets = {}
        for category_name, assets in assets_by_category.items():
            formatted_assets[category_name] = [
                {
                    "name": asset["name"],
                    "path": asset["path"],
                    "thumbnail": asset.get("thumbnail"),
                    "rotations": asset.get("rotations", {}),
                    "max": asset.get("max"),
                    "pair": asset.get("pair"),
                    "category": category_name,
                }
                for asset in assets
            ]
        return formatted_assets
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/packs/{pack_id}/")
def pack_detail(pack_id: str):
    try:
        packs = AssetIndexer.index_all_packs()
        pack = next((p for p in packs if p["id"] == pack_id), None)
        if not pack:
            raise HTTPException(status_code=404, detail="Pack not found")
        return {
            "id": pack["id"],
            "name": pack["name"],
            "image": pack.get("image"),
            "align": pack.get("align", 25),
            "gameType": get_pack_game_type(pack),
            "categories": list(pack["categories"].keys()),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
