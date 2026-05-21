"""
Chemins et répertoires du projet (sans Django).
Même logique qu’anciennement dans zombicide_editor/settings.py.
"""
from __future__ import annotations

import os
from pathlib import Path

# Racine du dépôt zproject/ (backend/ est un sous-dossier)
_BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = _BACKEND_DIR.parent

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

ASSETS_DIR = BASE_DIR / "assets"
BG_MAPEDITOR_TILES_DIR = BASE_DIR / "assets"
PACKS_DIR = MEDIA_ROOT / "packs"
USERS_DIR = MEDIA_ROOT / "users"

# CORS (mêmes origines qu’en Django)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]


def ensure_data_directories() -> None:
    """Crée les dossiers attendus s’ils n’existent pas."""
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(PACKS_DIR, exist_ok=True)
    os.makedirs(PACKS_DIR / "custom", exist_ok=True)
    os.makedirs(USERS_DIR, exist_ok=True)
    os.makedirs(USERS_DIR / "temp" / "maps", exist_ok=True)
