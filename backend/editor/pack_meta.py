"""
Métadonnées éditeur par pack : type de jeu choisi à l'upload.

Préférence : écrire `gameType=…` dans le fichier `cfg` à la racine du pack
(même format clé=valeur que Mapeditor). Si `cfg` est absent, repli sur
`editor_pack_meta.json` (rétrocompat).
"""
import json
from pathlib import Path

from django.conf import settings

from api.parsers.editor_game_types import normalize_editor_game_type

EDITOR_PACK_META_FILENAME = 'editor_pack_meta.json'


def _merge_game_type_into_cfg(cfg_path: Path, game_type: str) -> None:
    """Ajoute ou remplace la ligne gameType= dans le cfg racine."""
    text = cfg_path.read_text(encoding='utf-8')
    lines = text.splitlines()
    key_line = f'gameType={game_type}'
    out = []
    replaced = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('gameType=') or stripped.startswith('game_type='):
            if not replaced:
                out.append(key_line)
                replaced = True
            continue
        out.append(line.rstrip('\r'))
    if not replaced:
        out.append(key_line)
    new_text = '\n'.join(out)
    if not new_text.endswith('\n'):
        new_text += '\n'
    cfg_path.write_text(new_text, encoding='utf-8')


def write_pack_game_type(pack_id: str, game_type: str) -> None:
    """
    Persiste le type de jeu : dans `cfg` si possible, sinon JSON meta.
    """
    gt = normalize_editor_game_type(game_type)
    if not gt:
        return
    pid = str(pack_id or '').strip()
    if not pid or '..' in pid or '/' in pid or '\\' in pid:
        return
    pack_dir = Path(settings.ASSETS_DIR) / pid
    if not pack_dir.is_dir():
        return
    cfg_path = pack_dir / 'cfg'
    if cfg_path.is_file():
        _merge_game_type_into_cfg(cfg_path, gt)
        legacy = pack_dir / EDITOR_PACK_META_FILENAME
        if legacy.exists():
            try:
                legacy.unlink()
            except OSError:
                pass
        return
    path = pack_dir / EDITOR_PACK_META_FILENAME
    existing = {}
    if path.exists():
        try:
            with open(path, encoding='utf-8') as f:
                existing = json.load(f) or {}
        except Exception:
            existing = {}
    if not isinstance(existing, dict):
        existing = {}
    existing['gameType'] = gt
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
