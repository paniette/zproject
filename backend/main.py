"""
Application FastAPI — même contrat que l'ancien Django (port 8000, préfixe /api).
Lancer depuis le dossier backend/ :
  uvicorn main:app --reload --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

import app_config
from routes import files as routes_files
from routes import packs as routes_packs
from routes import users_maps as routes_users_maps


@asynccontextmanager
async def lifespan(_app: FastAPI):
    app_config.ensure_data_directories()
    yield


app = FastAPI(title="Zombicide editor API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(app_config.CORS_ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=str(app_config.MEDIA_ROOT)), name="media")
app.mount("/assets", StaticFiles(directory=str(app_config.ASSETS_DIR)), name="assets_root")
app.mount(
    "/bgmapeditor_tiles",
    StaticFiles(directory=str(app_config.BG_MAPEDITOR_TILES_DIR)),
    name="bgmapeditor_tiles",
)

app.include_router(routes_packs.router, prefix="/api")
app.include_router(routes_users_maps.router, prefix="/api")
app.include_router(routes_files.router, prefix="/api")
