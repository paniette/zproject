# Référence backend FastAPI (API + modules)

Ce document décrit l’**API REST** exposée sous le préfixe **`/api/`** (routeurs dans [`backend/routes/`](../backend/routes/), point d’entrée [`backend/main.py`](../backend/main.py)) et résume les **modules Python** (`api/parsers`, `editor`, `routes`). En développement, le frontend Vite proxy en général `/api` vers `http://127.0.0.1:8000`.

## Régénérer l’aperçu des symboles

La section « Modules Python (aperçu généré) » est produite à partir des **docstrings** du code :

```bash
python scripts/generate_backend_doc.py --write
```

Depuis la racine du dépôt (`zproject/`). Sans `--write`, le script affiche le même Markdown sur **stdout** (prévisualisation).

## Arborescence utile

```
backend/
├── app_config.py       # Chemins (ASSETS_DIR, MEDIA_ROOT, …), CORS, ensure_data_directories()
├── main.py             # FastAPI, CORS, StaticFiles, inclusion des routeurs /api
├── routes/             # Handlers HTTP (packs, users/maps, fichiers image)
├── api/
│   └── parsers/        # PackParser, indexation, types de jeu
└── editor/             # cartes, utilisateurs, upload ZIP / assets
```

## API REST (`/api/…`)

Les routes sont réparties dans [`backend/routes/packs.py`](../backend/routes/packs.py), [`backend/routes/users_maps.py`](../backend/routes/users_maps.py) et [`backend/routes/files.py`](../backend/routes/files.py). **L’ordre d’enregistrement** des routes packs est important : les segments littéraux (`custom`, `upload-zip`, `uploaded`, …) **doivent** rester avant `packs/{pack_id}` pour ne pas être pris pour un identifiant de pack.

| Méthode | Chemin (relatif à `/api/`) | Handler (module) | Rôle |
|--------|----------------------------|------------------|------|
| GET | `packs/` | `list_packs` | Liste les packs (ré-indexation), avec `gameType` enrichi si connu. |
| GET | `packs/{pack_id}/` | `pack_detail` | Métadonnées d’un pack et noms de catégories. |
| GET | `packs/{pack_id}/assets/` | `pack_assets` | Assets par catégorie (chemins, miniatures, rotations, max/pair). |
| POST | `packs/custom/upload/` | `custom_pack_upload` | Upload d’image custom + normalisation (tuile), option `game_type`. |
| GET | `packs/custom/` | `list_custom_packs` | Liste des packs sous `packs/custom`. |
| POST | `packs/upload-zip/` | `pack_zip_upload` | Import ZIP pack vers le répertoire assets ; option `game_type`. |
| GET | `packs/uploaded/` | `list_uploaded_packs` | Liste des packs présents dans le dossier médias assets. |
| DELETE | `packs/uploaded/{pack_id}/` | `delete_uploaded_pack` | Supprime le dossier du pack dans `ASSETS_DIR`. |
| GET | `assets/{asset_path}` | `get_asset` | Sert un fichier image (PNG) depuis assets ou `bgmapeditor_tiles`. |
| GET | `users/` | `list_users` | Liste les utilisateurs (dossiers sous `USERS_DIR`). |
| POST | `users/` | `create_user` | Crée l’arborescence d’un utilisateur temporaire (`username`). |
| GET | `users/{username}/maps/` | `list_user_maps` | Liste les cartes JSON de l’utilisateur. |
| POST | `users/{username}/maps/` | `create_map` | Crée une carte (corps JSON = données carte). |
| GET | `users/{username}/maps/{map_id}/` | `get_map` | Lit une carte. |
| PUT | `users/{username}/maps/{map_id}/` | `update_map` | Met à jour une carte. |
| DELETE | `users/{username}/maps/{map_id}/` | `delete_map` | Supprime le fichier carte. |
| GET | `maps/public/` | `public_maps` | Liste toutes les cartes de tous les utilisateurs. |

Le serveur monte aussi les répertoires **`/media`**, **`/assets`**, **`/bgmapeditor_tiles`** (fichiers statiques), comme le faisait l’ancien Django en développement.

## Configuration

| Fichier | Rôle |
|---------|------|
| [`app_config.py`](../backend/app_config.py) | `BASE_DIR`, `ASSETS_DIR`, `MEDIA_ROOT`, `USERS_DIR`, `PACKS_DIR`, CORS, création des dossiers. |
| [`main.py`](../backend/main.py) | Application FastAPI, middleware CORS, `StaticFiles`, inclusion des routeurs. |

## Corps JSON (cartes)

Le flux des cartes repose sur des **dicts JSON** libres passés à `MapManager` (création / mise à jour) ; pas de schéma Pydantic imposé côté API pour rester aligné avec le frontend.

<!-- GEN:BEGIN -->
## Modules Python (aperçu généré)

Bloc régénéré par `python scripts/generate_backend_doc.py --write`. Chaque entrée reprend la **première ligne de docstring** du symbole ; sinon *non documenté*.

*Dernière génération : 2026-05-14 15:35 UTC*

### `backend/api/parsers/__init__.py`
- *(aucun symbole public listé — uniquement imports / assignations)*

### `backend/api/parsers/asset_indexer.py`
*Module : Asset indexer - wrapper for pack parsing*

- class `AssetIndexer` — Index all packs in assets directory
- `AssetIndexer.index_all_packs()` — Index all packs in the assets directory (and legacy bgmapeditor_tiles)
- `AssetIndexer.get_pack_assets()` — Get assets for a specific pack

### `backend/api/parsers/editor_game_types.py`
*Module : Types de jeu reconnus par l'éditeur (filtres UI, cfg racine, meta).*

- `normalize_editor_game_type()` — Retourne un id normalisé ou None si invalide / 'all'.

### `backend/api/parsers/pack_parser.py`
*Module : Parser for Zombicide Mapeditor pack files (cfg format)*

- `get_base_dir()` — Get the base directory for relative paths
- class `PackParser` — Parse Mapeditor pack structure and cfg files
- `PackParser.__init__()` — pack_dir : chemin dossier racine du pack (contient au minimum cfg ou catégories).
- `PackParser.parse_pack()` — Parse a complete pack and return its structure
- `PackParser._parse_category()` — Parse a category directory (e.g., 01.tiles)
- `PackParser._scan_category_assets()` — Scan category directory for assets
- `PackParser._find_rotations()` — Find rotation images for an asset
- `PackParser._find_rotations_in_dir()` — Find rotation images in asset directory
- `PackParser._find_thumbnail()` — Find thumbnail for an asset
- `PackParser._find_thumbnail_in_dir()` — Find thumbnail in asset directory
- `PackParser._parse_cfg_file()` — Parse a cfg file and return a dict
- `PackParser._parse_max_string()` — Parse max string like 'file.png:1;file2.png:2'
- `PackParser._parse_pairs_string()` — Parse pairs string like 'file1.png:file2.png;file3.png:file4.png'

### `backend/app_config.py`
*Module : Chemins et répertoires du projet (sans Django).*

- `ensure_data_directories()` — Crée les dossiers attendus s’ils n’existent pas.

### `backend/editor/file_watcher.py`
*Module : File watcher for detecting changes in bgmapeditor_tiles directory*

- class `PackChangeHandler` — Handle file system events for pack changes
- `PackChangeHandler.__init__()` — callback : fonction optionnelle appelée à chaque événement fichier.
- `PackChangeHandler.on_created()` — *non documenté*
- `PackChangeHandler.on_modified()` — *non documenté*
- `PackChangeHandler.on_moved()` — *non documenté*
- `PackChangeHandler.on_deleted()` — *non documenté*
- `PackChangeHandler._notify_change()` — Notify about a change in the packs directory
- class `PackFileWatcher` — Watch for changes in bgmapeditor_tiles directory
- `PackFileWatcher.__init__()` — Observer inactif jusqu'à start() ; callbacks listés dans callbacks.
- `PackFileWatcher.start()` — Start watching the directory
- `PackFileWatcher.stop()` — Stop watching
- `PackFileWatcher._handle_change()` — Handle a file system change
- `PackFileWatcher.add_callback()` — Add a callback function to be called on changes
- `get_watcher()` — Get or create the global file watcher instance

### `backend/editor/map_manager.py`
*Module : Map manager for saving/loading maps as JSON files*

- class `MapManager` — Manage map files (JSON) for users
- `MapManager.__init__()` — *non documenté*
- `MapManager.create_map()` — Create a new map
- `MapManager.update_map()` — Update an existing map
- `MapManager.get_map()` — Get a map by ID
- `MapManager.delete_map()` — Delete a map
- `MapManager.list_maps()` — List all maps for this user
- `MapManager.list_all_public_maps()` — List all maps from all users (public)

### `backend/editor/pack_meta.py`
*Module : Métadonnées éditeur par pack : type de jeu choisi à l'upload.*

- `_merge_game_type_into_cfg()` — Ajoute ou remplace la ligne gameType= dans le cfg racine.
- `write_pack_game_type()` — Persiste le type de jeu : dans `cfg` si possible, sinon JSON meta.

### `backend/editor/pack_uploader.py`
*Module : Upload and normalize custom pack assets*

- `sanitize_asset_name()` — Safe folder name under pack/category (no path traversal).
- `sanitize_path_segment()` — Valide un segment de chemin (pack, catégorie) contre traversal et caractères dangereux.
- class `PackUploader` — Handle upload and normalization of custom pack assets
- `PackUploader.__init__()` — pack_name : id dossier pack sous ASSETS_DIR (créé si besoin).
- `PackUploader.upload_and_normalize()` — Upload an image and normalize it (create rotations and thumbnail).
- `PackUploader._update_category_cfg()` — Update or create cfg file for category
- `PackUploader._update_pack_cfg()` — Update or create pack root cfg file
- `PackUploader.create_pack()` — Create a new custom pack in /assets/ directory

### `backend/editor/pack_zip_uploader.py`
*Module : Upload and extract ZIP packs*

- class `PackZipUploader` — Handle upload and extraction of ZIP packs
- `PackZipUploader.upload_and_extract()` — Upload and extract a ZIP pack
- `PackZipUploader.list_uploaded_packs()` — List all uploaded packs in assets directory
- `PackZipUploader.delete_uploaded_pack()` — Delete an uploaded pack from assets directory

### `backend/editor/user_manager.py`
*Module : User manager for temporary users*

- class `UserManager` — Manage temporary users
- `UserManager.ensure_user()` — Ensure a user directory exists
- `UserManager.list_users()` — List all available users
- `UserManager.create_user()` — Create a new user directory
- `UserManager.user_exists()` — Check if a user exists

### `backend/editor/utils.py`
*Module : Utility functions for the editor module.*

- `ensure_directory()` — Create directory if it doesn't exist.

### `backend/main.py`
*Module : Application FastAPI — même contrat que l'ancien Django (port 8000, préfixe /api).*

- `lifespan()` — *non documenté*

### `backend/routes/__init__.py`
- *(aucun symbole public listé — uniquement imports / assignations)*

### `backend/routes/files.py`
*Module : Sert les images sous /api/assets/ (même logique que l'ancienne AssetView).*

- `get_asset()` — *non documenté*

### `backend/routes/packs.py`
*Module : Routes /api/packs/* et uploads (ordre des routes = même contrainte que l'ancien urls.py Django).*

- `list_packs()` — *non documenté*
- `custom_pack_upload()` — *non documenté*
- `list_custom_packs()` — *non documenté*
- `pack_zip_upload()` — *non documenté*
- `list_uploaded_packs()` — *non documenté*
- `delete_uploaded_pack()` — *non documenté*
- `pack_assets()` — *non documenté*
- `pack_detail()` — *non documenté*

### `backend/routes/packs_helpers.py`
*Module : Helpers partagés pour les routes packs (index statique packs-index.json).*

- `load_pack_game_types_from_static_index()` — Source de vérité partagée avec le build statique: packs-index.json.
- `get_pack_game_type()` — Priorité: pack['gameType'] puis mapping du static index.
- `parse_form_bool()` — Interprète une valeur issue d'un formulaire (bool ou chaîne).

### `backend/routes/users_maps.py`
*Module : Routes /api/users/* et /api/maps/public/.*

- `list_users()` — *non documenté*
- `create_user()` — *non documenté*
- `list_user_maps()` — *non documenté*
- `create_map()` — *non documenté*
- `get_map()` — *non documenté*
- `update_map()` — *non documenté*
- `delete_map()` — *non documenté*
- `public_maps()` — *non documenté*

<!-- GEN:END -->
