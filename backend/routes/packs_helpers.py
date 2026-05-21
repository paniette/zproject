"""Helpers partagés pour les routes packs (index statique packs-index.json)."""
from __future__ import annotations

import json
from functools import lru_cache

import app_config


@lru_cache(maxsize=1)
def load_pack_game_types_from_static_index() -> dict[str, str]:
    """
    Source de vérité partagée avec le build statique: packs-index.json.
    Retourne un dict { packId: gameType }.
    """
    try:
        index_path = app_config.BASE_DIR / "packs-index.json"
        if not index_path.exists():
            return {}
        with open(index_path, encoding="utf-8") as f:
            data = json.load(f) or {}
        packs = data.get("packs") or []
        if not isinstance(packs, list):
            return {}
        m: dict[str, str] = {}
        for p in packs:
            if not isinstance(p, dict):
                continue
            pid = p.get("id")
            gt = p.get("gameType")
            if isinstance(pid, str) and isinstance(gt, str) and pid and gt:
                m[pid] = gt
        return m
    except Exception:
        return {}


def get_pack_game_type(pack: dict) -> str | None:
    """Priorité: pack['gameType'] puis mapping du static index."""
    try:
        gt = pack.get("gameType")
        if isinstance(gt, str) and gt:
            return gt
    except Exception:
        pass
    return load_pack_game_types_from_static_index().get(pack.get("id"))


def parse_form_bool(value) -> bool:
    """Interprète une valeur issue d'un formulaire (bool ou chaîne)."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    s = str(value).lower().strip()
    return s in ("true", "1", "yes", "on")
