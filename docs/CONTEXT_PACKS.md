# Annexe — Packs Mapeditor & index statique

Format packs Windows, `gameType`, génération JSON pour le mode statique. Retour : [`CONTEXT.md`](CONTEXT.md). API détaillée : [`BACKEND_REFERENCE.md`](BACKEND_REFERENCE.md).

---

## Structure pack (Mapeditor)

À la racine : `cfg`, `guillotine.png`, `licence`, dossiers :

- `01.tiles/` — sol (recto/verso, `r_0.png` … `r_thumb.png`)
- `02.doors/`, `04.other tokens/`, `05.zombies/`, etc.

Clés `cfg` typiques : `name`, `max`, `pairs`, `z-index`, `align`, optionnel **`gameType=`**.

Emplacements disque :

- Dev / référence : `bgmapeditor_tiles/`
- Backend : `backend/media/` / `ASSETS_DIR` (`app_config.py`)
- Statique : chemins dans `packs-index.json`, servis en relatif depuis la racine du site

---

## Type de jeu (`gameType`)

| Étape | Détail |
|-------|--------|
| Source de vérité | Ligne **`gameType=`** (ou `game_type=`) dans le **`cfg` racine** du pack. |
| Valeurs | `classic`, `modern`, `fantasy`, `western`, `scifi`, `night` — normalisation : `backend/api/parsers/editor_game_types.py`. |
| Rétrocompat | Sans `gameType` dans `cfg` → lecture `editor_pack_meta.json` (uploads anciens). |
| Upload API | Front envoie `game_type` → `backend/editor/pack_meta.py` écrit le `cfg`. |
| Index statique | `scripts/generate_packs_index.py` → `gameType` dans `packs-index.json` ; défaut JSON **`fantasy`** si absent sur disque. |
| Backfill | `scripts/backfill_cfg_game_type.py` déduit le type depuis le nom de dossier pack. |

**Frontend** : filtre Packs & Assets via `themeStore.assetGameTypeFilter` / `config/gameTypes.js`.  
**≠ `mission.pageTheme`** : même enum de séries, rôles différents — voir [`CONTEXT.md`](CONTEXT.md).

---

## Backend parsing

- `backend/api/parsers/pack_parser.py`, `asset_indexer.py`
- `backend/editor/file_watcher.py` — re-index optionnelle (watchdog)
- Routes : `backend/routes/packs.py`, images `backend/routes/files.py`

---

## Index statique (sans Python)

```bash
cd scripts
python generate_packs_index.py
python generate_maps_index.py
```

Produit sous `frontend/public/` :

| Fichier | Contenu |
|---------|---------|
| `packs-index.json` | Liste packs + assets inline |
| `maps-index.json` | Métadonnées cartes |
| `maps/*.json` | Corps complet scénarios (ex. `author: temp`) |

Workflow build FTP : skill `.cursor/skills/zproject-prep-static-ftp`.

---

## Cartes JSON (hors mission)

Champs carte : `version`, `name`, `pack`, `grid`, `gridOffsetX/Y`, `layers`, `metadata` (`author`, dates), **`mission`**.

API mode complet : `/api/users/<username>/maps/` — voir `BACKEND_REFERENCE.md`.
