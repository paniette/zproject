"""
Ajoute gameType=… dans le cfg racine de chaque pack sous assets/,
uniquement si le type n’est pas déjà défini (cfg ou meta).

Le type est déduit du **nom du dossier** (id pack), avec la même logique
qu’historiquement dans infer_game_type (Mapeditor / gammes Zombicide).

Usage (racine du dépôt) :
  py scripts/backfill_cfg_game_type.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zombicide_editor.settings')

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402

from api.parsers.pack_parser import PackParser  # noqa: E402
from editor.pack_meta import write_pack_game_type  # noqa: E402


def infer_game_type_from_pack_id(pack_id: str) -> str:
    """Déduit le type de jeu depuis l’id du pack (= nom du dossier sous assets/)."""
    pid = (pack_id or '').upper()

    if pid.endswith('-A5-2E') or pid.endswith('-A6-ZC') or pid.endswith('-A7-FH'):
        return 'modern'

    if pid.startswith('G-ZOMBICIDE-IV'):
        return 'scifi'

    # Night of the Living Dead — avant Western (D1-LD matche aussi G-ZOMBICIDE-D1)
    if (
        pid.startswith('E1_')
        or 'NIGHT' in pid
        or pid.endswith('-LD')
        or '-LD' in pid
        or 'LIVING' in pid
    ):
        return 'night'

    if pid.startswith('G-ZOMBICIDE-D1') or pid.startswith('D1_') or 'UNDEAD' in pid:
        return 'western'

    if (
        pid.startswith('G-ZOMBICIDE-BP')
        or pid.startswith('G-ZOMBICIDE-WD')
        or pid.startswith('G-ZOMBICIDE-EE')
        or pid.startswith('G-ZOMBICIDE-TMNT')
    ):
        return 'fantasy'

    if (
        pid.startswith('G-ZOMBICIDE-B2-')
        or pid.startswith('G-ZOMBICIDE-B4-')
        or pid.startswith('G-ZOMBICIDE-B5-')
        or pid == 'G-ZOMBICIDE-BBWB'
    ):
        return 'fantasy'

    if (
        pid.startswith('G-ZOMBICIDE-PO')
        or pid.startswith('G-ZOMBICIDE-RM')
        or pid.startswith('G-ZOMBICIDE-TCM')
        or pid.startswith('G-ZOMBICIDE-AN')
    ):
        return 'classic'

    if pid == 'G-ZOMBICIDE':
        return 'classic'

    if pid.startswith('G-ZOMBICIDE'):
        return 'classic'

    return 'fantasy'


def main():
    assets_dir = Path(settings.ASSETS_DIR)
    if not assets_dir.is_dir():
        print(f'ASSETS_DIR introuvable : {assets_dir}')
        sys.exit(1)

    updated = 0
    skipped = 0
    errors = 0

    for item in sorted(assets_dir.iterdir(), key=lambda p: p.name.lower()):
        if not item.is_dir() or item.name.startswith('.'):
            continue
        if not (item.name.startswith('G-Zombicide-') or (item / 'cfg').exists()):
            continue

        pack_id = item.name
        cfg = item / 'cfg'
        if not cfg.is_file():
            skipped += 1
            continue

        try:
            info = PackParser(item).parse_pack()
        except Exception as e:
            print(f'{pack_id}: erreur parse {e}')
            errors += 1
            continue

        if info.get('gameType'):
            skipped += 1
            continue

        game_type = infer_game_type_from_pack_id(pack_id)
        write_pack_game_type(pack_id, game_type)
        print(f'+ {pack_id} -> {game_type} (déduit du nom du dossier)')
        updated += 1

    print(f'Terminé : {updated} pack(s) mis à jour, {skipped} ignoré(s), {errors} erreur(s).')


if __name__ == '__main__':
    main()
