"""Sert les images sous /api/assets/ (même logique que l'ancienne AssetView)."""
from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException

import app_config

router = APIRouter(tags=["assets"])


@router.get("/assets/{asset_path:path}")
def get_asset(asset_path: str):
    path = asset_path
    if path.startswith("assets/"):
        path = path[7:]
        full_path = os.path.join(app_config.ASSETS_DIR, path)
    elif path.startswith("bgmapeditor_tiles/"):
        path = path[18:]
        full_path = os.path.join(app_config.BG_MAPEDITOR_TILES_DIR, path)
    else:
        full_path = os.path.join(app_config.ASSETS_DIR, path)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            full_path = os.path.join(app_config.BG_MAPEDITOR_TILES_DIR, path)

    if os.path.exists(full_path) and os.path.isfile(full_path):
        from starlette.responses import FileResponse

        return FileResponse(full_path, media_type="image/png")

    raise HTTPException(status_code=404, detail=f"Asset not found: {asset_path}")
