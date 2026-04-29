# Référence backend Django (API + modules)

Ce document décrit l’**API REST** exposée sous le préfixe **`/api/`** (voir [`backend/zombicide_editor/urls.py`](../backend/zombicide_editor/urls.py)) et résume les **modules Python** (`api`, `editor`, parsers). En développement, le frontend Vite proxy en général `/api` vers `http://127.0.0.1:8000`.

## Régénérer l’aperçu des symboles

La section « Modules Python (aperçu généré) » est produite à partir des **docstrings** du code :

```bash
python scripts/generate_backend_doc.py --write
```

Depuis la racine du dépôt (`zproject/`). Sans `--write`, le script affiche le même Markdown sur **stdout** (prévisualisation).

## Arborescence utile

```
backend/
├── zombicide_editor/   # settings, urls racine, WSGI/ASGI
├── api/                # vues DRF, routes, serializers
│   └── parsers/        # PackParser, indexation, types de jeu
├── editor/             # cartes, utilisateurs, upload ZIP / assets
└── manage.py
```

## API REST (`/api/…`)

Toutes les routes sont définies dans [`backend/api/urls.py`](../backend/api/urls.py). L’ordre des `path()` est important : les segments littéraux (`custom`, `upload-zip`, etc.) **doivent** rester avant `packs/<pack_id>/` pour ne pas être interprétés comme un `pack_id`.

| Méthode | Chemin (relatif à `/api/`) | Classe (vue) | Rôle |
|--------|----------------------------|--------------|------|
| GET | `packs/` | `PackListView` | Liste les packs (ré-indexation), avec `gameType` enrichi si connu. |
| GET | `packs/<pack_id>/` | `PackDetailView` | Métadonnées d’un pack et noms de catégories. |
| GET | `packs/<pack_id>/assets/` | `PackAssetsView` | Assets par catégorie (chemins, miniatures, rotations, max/pair). |
| POST | `packs/custom/upload/` | `CustomPackUploadView` | Upload d’image custom + normalisation (tuile), option `game_type`. |
| GET | `packs/custom/` | `CustomPackListView` | Liste des packs sous `packs/custom`. |
| POST | `packs/upload-zip/` | `PackZipUploadView` | Import ZIP pack vers le répertoire assets ; option `game_type`. |
| GET | `packs/uploaded/` | `UploadedPackListView` | Liste des packs présents dans le dossier médias assets. |
| DELETE | `packs/uploaded/<pack_id>/` | `UploadedPackDeleteView` | Supprime le dossier du pack dans `ASSETS_DIR`. |
| GET | `assets/<path:asset_path>` | `AssetView` | Sert un fichier image (PNG) depuis assets ou `bgmapeditor_tiles`. |
| GET | `users/` | `UserListView` | Liste les utilisateurs (dossiers sous `USERS_DIR`). |
| POST | `users/` | `UserListView` | Crée l’arborescence d’un utilisateur temporaire (`username`). |
| GET | `users/<username>/maps/` | `UserMapsView` | Liste les cartes JSON de l’utilisateur. |
| POST | `users/<username>/maps/` | `UserMapsView` | Crée une carte (corps JSON = données carte). |
| GET | `users/<username>/maps/<map_id>/` | `MapDetailView` | Lit une carte. |
| PUT | `users/<username>/maps/<map_id>/` | `MapDetailView` | Met à jour une carte. |
| DELETE | `users/<username>/maps/<map_id>/` | `MapDetailView` | Supprime le fichier carte. |
| GET | `maps/public/` | `PublicMapsView` | Liste toutes les cartes de tous les utilisateurs. |

En **DEBUG**, le projet sert aussi les médias configurés dans `settings` (fichiers médias, `/assets/`, `/bgmapeditor_tiles/` selon [`backend/zombicide_editor/urls.py`](../backend/zombicide_editor/urls.py)).

## Configuration projet (`zombicide_editor`)

| Fichier | Rôle |
|---------|------|
| `settings.py` | Chemins `ASSETS_DIR`, `USERS_DIR`, packs, `INSTALLED_APPS` (`api`, `editor`), DRF, etc. |
| `urls.py` | Monte `admin/`, inclut `api.urls` sous `api/`, raccourcis `static()` en développement. |
| `wsgi.py` / `asgi.py` | Points d’entrée serveur WSGI/ASGI. |

## Schémas DRF

[`backend/api/serializers.py`](../backend/api/serializers.py) définit des serializers **légers** (surtout placeholder / validation partielle). Le flux principal des cartes repose sur des **dicts JSON** sérialisés manuellement dans les vues et `MapManager`.

<!-- GEN:BEGIN -->
## Modules Python (aperçu généré)

Bloc régénéré par `python scripts/generate_backend_doc.py --write`. Chaque entrée reprend la **première ligne de docstring** du symbole ; sinon *non documenté*.

*Dernière génération : 2026-04-29 22:12 UTC*

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

### `backend/api/serializers.py`
*Module : Schémas DRF minimaux (validation côté API ; la plupart des payloads sont des dicts JSON libres).*

- class `PackSerializer` — Champs id / nom / image pour représentation pack (usage réservé ou futur).
- class `AssetSerializer` — Représentation simplifiée d'un asset (nom, chemin, catégorie).
- class `MapSerializer` — Structure carte : grille, couches, métadonnées mission (alignée sur le JSON éditeur).

### `backend/api/urls.py`
- *(aucun symbole public listé — uniquement imports / assignations)*

### `backend/api/views.py`
- `_load_pack_game_types_from_static_index()` — Source de vérité partagée avec le build statique: `packs-index.json`.
- `_get_pack_game_type()` — Résout le type de jeu d'un pack.
- class `PackListView` — Liste les packs disponibles (ré-indexation à chaque requête).
- `PackListView.get()` — List all available packs
- class `PackDetailView` — Détail d'un pack : nom, image, align, type de jeu, liste des catégories.
- `PackDetailView.get()` — Get details of a specific pack
- class `PackAssetsView` — Assets d'un pack groupés par catégorie (chemins, miniatures, rotations).
- `PackAssetsView.get()` — Get assets for a specific pack, organized by category
- class `AssetView` — Sert un fichier image (PNG) depuis ASSETS_DIR ou BG_MAPEDITOR_TILES_DIR.
- `AssetView.get()` — Stream binaire d'une image pack / tuile.
- class `UserListView` — Utilisateurs « temporaires » (dossiers sous USERS_DIR).
- `UserListView.get()` — List all temporary users
- `UserListView.post()` — Create a new temporary user
- class `UserMapsView` — CRUD de liste : cartes JSON d'un utilisateur donné.
- `UserMapsView.get()` — List all maps for a user
- `UserMapsView.post()` — Create a new map for a user
- class `MapDetailView` — Lecture, mise à jour et suppression d'une carte JSON par id.
- `MapDetailView.get()` — Get a specific map
- `MapDetailView.put()` — Update a map
- `MapDetailView.delete()` — Delete a map
- class `PublicMapsView` — Agrège toutes les cartes de tous les utilisateurs (aperçu / galerie).
- `PublicMapsView.get()` — List all public maps (from all users)
- class `CustomPackUploadView` — Upload d'image personnalisée : redimensionnement, rotations, entrée cfg.
- `CustomPackUploadView.post()` — Upload and normalize a custom asset
- class `CustomPackListView` — Liste les packs du répertoire `packs/custom` (métadonnées via PackParser).
- `CustomPackListView.get()` — List custom packs
- class `PackZipUploadView` — Import d'un pack ZIP Mapeditor vers ASSETS_DIR (validation structure).
- `PackZipUploadView.post()` — Upload and extract a ZIP pack
- class `UploadedPackListView` — Liste les dossiers-pack présents sous le répertoire médias « assets ».
- `UploadedPackListView.get()` — List uploaded packs
- class `UploadedPackDeleteView` — Supprime un pack uploadé (dossier sous ASSETS_DIR) par identifiant.
- `UploadedPackDeleteView.delete()` — Delete an uploaded pack from assets directory

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

### `backend/zombicide_editor/__init__.py`
- *(aucun symbole public listé — uniquement imports / assignations)*

### `backend/zombicide_editor/asgi.py`
*Module : ASGI config for zombicide_editor project.*

- *(aucun symbole public listé — uniquement imports / assignations)*

### `backend/zombicide_editor/settings.py`
*Module : Django settings for zombicide_editor project.*

- *(aucun symbole public listé — uniquement imports / assignations)*

### `backend/zombicide_editor/urls.py`
*Module : URL configuration for zombicide_editor project.*

- *(aucun symbole public listé — uniquement imports / assignations)*

### `backend/zombicide_editor/wsgi.py`
*Module : WSGI config for zombicide_editor project.*

- *(aucun symbole public listé — uniquement imports / assignations)*

<!-- GEN:END -->
