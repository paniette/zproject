# Contexte projet — Éditeur de cartes Zombicide (web)

Document de référence pour reprendre le développement. Il synthétise les plans Cursor « Éditeur Zombicide Web » et « Correction interactions éditeur carte », ainsi que le README racine.

---

## Objectif

Éditeur web de cartes **Zombicide** compatible avec les packs du **Mapeditor Windows** : structure de dossiers et fichiers `cfg`, import ZIP, édition sur canvas (tuiles, portes, tokens, zombies), sauvegarde en **JSON** (sans base de données métier), **utilisateurs temporaires**, export image.

---

## Stack

| Couche | Technologies |
|--------|----------------|
| Frontend | Vue.js 3 (Composition API), Vite, Pinia |
| Backend | Django, Django REST Framework, CORS |
| Persistance | Fichiers JSON (ex. sous `media/users/`) |
| Traitement images | Pillow (PIL) côté backend |

---

## Mode statique (sans Django)

L’éditeur peut tourner **sans backend** pour démo, OVH statique ou `npm run build` déployé seul.

| Élément | Rôle |
|--------|------|
| [`frontend/src/config.js`](frontend/src/config.js) | `VITE_STATIC_MODE` : par défaut **activé** sauf si la variable vaut explicitement `'false'` au build. |
| [`frontend/src/services/api.js`](frontend/src/services/api.js) | Si `config.staticMode`, packs / cartes / utilisateurs passent par **`fetch`** sur des JSON statiques (`packs-index.json`, `maps-index.json`, `localStorage` via `localStorageService`). Pas d’appels Django. |
| Build | `npm run build` génère `editor.html` + assets ; les chemins relatifs doivent rester cohérents avec l’hébergement. |
| Upload ZIP / élément | Boutons masqués en `staticMode` dans l’UI ; l’upload nécessite l’API Django. |

**Règle pour les évolutions** : toute nouvelle fonctionnalité qui appelle l’API doit prévoir une **branche statique** (données locales, JSON, ou message « non disponible hors ligne ») pour ne pas casser le déploiement statique.

---

## Arborescence utile

```
.
├── backend/                 # Django
│   ├── zombicide_editor/    # settings, urls, wsgi
│   ├── api/                 # REST, parsers (pack_parser, etc.)
│   ├── editor/              # map_manager, user_manager, file_watcher, uploaders
│   └── manage.py
├── frontend/
│   └── src/
│       ├── components/      # MapEditor, AppHeader, CanvasGrid, AssetPanel, …
│       ├── stores/          # mapStore, toolStore, userStore, packs/assets
│       ├── services/        # api.js, canvasRenderer.js
│       └── utils/
├── bgmapeditor_tiles/       # Packs décompressés (référence Mapeditor)
├── requirements.txt
└── README.md
```

Les médias packs/cartes peuvent aussi vivre sous `backend/media/` selon la configuration Django.

---

## Format des packs (Mapeditor)

À la racine d’un pack : `cfg`, `guillotine.png`, `licence`, puis des dossiers du type :

- `01.tiles/` — sol (souvent recto/verso, rotations `r_0.png`, `r_90.png`, …, `r_thumb.png`)
- `02.doors/`
- `04.other tokens/` (spawn, exit, objectives, …)
- `05.zombies/`
- autres catégories selon le pack

Les fichiers `cfg` portent typiquement : `name`, `max`, `pairs`, `z-index`, `align`.

#### Type de jeu (`gameType`, filtre Packs & Assets)

- **Source de vérité sur disque** : dans le **`cfg` à la racine du pack**, clé optionnelle **`gameType=`** (ou `game_type=`). Valeurs reconnues : `classic`, `modern`, `fantasy`, `western`, `scifi`, `night` — normalisation dans `backend/api/parsers/editor_game_types.py`.
- **Rétrocompat** : si le `cfg` ne définit pas encore le type, le parser peut lire **`editor_pack_meta.json`** à la racine du pack (uploads anciens).
- **Upload** (ZIP ou asset custom) : le front envoie **`game_type`** ; `backend/editor/pack_meta.py` met à jour la ligne dans le **`cfg`** (et supprime le meta legacy lorsque le `cfg` est mis à jour).
- **Index statique** : `scripts/generate_packs_index.py` s’appuie sur `PackParser` / `AssetIndexer` → le champ **`gameType`** de `packs-index.json` reflète ce qui est lu sur disque ; si absent, défaut **`fantasy`** dans le JSON uniquement.
- **Pré-remplissage des `cfg` sans type** : `scripts/backfill_cfg_game_type.py` parcourt `assets/`, déduit le type depuis le **nom du dossier** (logique alignée sur les ids Mapeditor), puis écrit `gameType=` si besoin.

**Backend** : parsing et index dans `api/parsers/pack_parser.py` ; surveillance optionnelle via `editor/file_watcher.py` (watchdog) pour re-indexer après changements sur le disque.

**API (vue d’ensemble)** : lister les packs, détail, assets par catégorie, servir les images (chemins exacts dans `backend/api/`).

---

## Frontend — écran principal

- **`MapEditor.vue`** — Layout ~25 % panneau gauche / 75 % canvas.
- **`AppHeader.vue`** — Utilisateur temporaire, charger carte, sauvegarder (dont Ctrl+S), export image.
- **`AssetPanel.vue`** — Hiérarchie packs → catégories → miniatures ; drag & drop et/ou clic pour placer.
- **`CanvasGrid.vue`** — Canvas HTML5, grille, zoom, pan, placement, sélection, halos de survol/sélection (voir section interactions).
- **`MapLoader.vue`**, **`UserSelector.vue`**, uploaders de packs (image / ZIP) selon les besoins.

**Stores principaux** :

- **`mapStore`** — `currentPack`, taille de grille, `tileSize`, `layers.tiles` / `layers.objects`, sélection, historique (undo/redo prévu), **`gridOffsetX` / `gridOffsetY`** (voir ci-dessous).
- **`toolStore`** — Outil actif : **`move`**, `rotate`, `delete` (plus d’outil « place » séparé).

---

## Format JSON d’une carte (référence)

Champs typiques : `version`, `name`, `pack`, `grid` (width, height, tileSize), `layers.tiles` (x, y, asset, rotation), `layers.objects` (id, type, asset, x, y, rotation, properties), `metadata` (created, modified, **author** = utilisateur temporaire, ex. `camp`).

**API cartes** : chemins du type `/api/users/<username>/maps/` pour CRUD ; possibilité de lister des cartes « publiques » / tous utilisateurs selon l’implémentation.

---

## Interactions canvas (plan « correction interactions »)

Ces choix sont **normatifs** pour éviter les régressions lors de modifications dans `CanvasGrid.vue`, `mapStore`, `canvasRenderer.js`, `Toolbar.vue`, `toolStore.js`.

### Offset global de grille

- État : **`gridOffsetX`**, **`gridOffsetY`** dans `mapStore`, action **`setGridOffset(x, y)`**.
- Le **pan** déplace cet offset : la **grille et tous les éléments** se déplacent ensemble.
- Position monde (concept) : coordonnées grille × `tileSize` + offset.

### Outils unifiés

- L’outil **« place »** a été **fusionné** avec **« move »** :
  - Clic sur un élément → sélection + déplacement (drag).
  - Clic sur case vide avec un **asset sélectionné** → placement + sélection de l’élément créé.
  - Sinon (vide, pas d’asset) → **pan** de la grille (offset).

### Sélection

- Clic : sélection cohérente des tuiles/objets (sauf cas **delete** qui supprime sans focus sélection si tel est le comportement retenu).
- Après **drag & drop** depuis le panneau : **sélection automatique** du nouvel élément.
- **Hover-to-selection** : l’élément **survolé** (`hoveredItem`) est pris en compte au clic avant l’action.

### Coordonnées

- **`getGridCoordinates`** / **`getGridCoordinatesWithSnap`** dans `canvasRenderer.js` doivent intégrer **`gridOffsetX/Y`** (et le zoom / tout décalage « vue » encore utilisé).

### Zoom

- Zoom via transformation canvas (`scale`, etc.) : grille et éléments doivent rester **cohérents** ; les tests manuels couvrent zoom + pan + placement.

### Feedback visuel

- **Survol** : halo bleu (`drawHover` ou équivalent), curseur selon outil (`move`, `delete`, `rotate`).
- **Sélection** : halo rouge plus visible (fond + contour).

---

## Backend métier (rappel)

| Module | Rôle |
|--------|------|
| `editor/map_manager.py` | Sauvegarde / chargement cartes JSON |
| `editor/user_manager.py` | Utilisateurs temporaires, dossiers par nom |
| `editor/pack_uploader.py` | Upload image, normalisation (rotations, thumbs) |
| `editor/pack_zip_uploader.py` | ZIP complet, validation, décompression |
| `editor/file_watcher.py` | Détection changements sur les assets |

Export image : souvent côté client (`canvas.toDataURL`, etc.) ; export serveur possible (Pillow) si implémenté.

---

## Démarrage local

**Backend** (`README`) :

```bash
cd backend
pip install -r ../requirements.txt
python manage.py migrate   # souvent minimal sans BD métier
python manage.py runserver
```

**Frontend** :

```bash
cd frontend
npm install
npm run dev
```

Application dev typiquement sur **http://localhost:5173**. Placer les packs dans **`bgmapeditor_tiles/`** puis utiliser l’UI (sélection pack, drag & drop, Ctrl+S, export).

---

## Fichiers pivots pour coder

| Sujet | Fichiers |
|-------|----------|
| Canvas, pan, zoom, sélection | `frontend/src/components/CanvasGrid.vue` |
| État carte, offset grille, undo/redo, aperçu | `frontend/src/stores/mapStore.js` |
| Outils | `frontend/src/stores/toolStore.js`, `frontend/src/components/Toolbar.vue` |
| Propriétés sélection | `frontend/src/components/PropertyPanel.vue` |
| Versions locales (après sauvegarde) | `frontend/src/services/mapVersions.js`, `MapVersionsModal.vue` |
| Collaboration temps réel (hors scope court terme) | `docs/COLLABORATION.md` |
| Coordonnées écran ↔ grille | `frontend/src/services/canvasRenderer.js` |
| Assets / API | `frontend/src/components/AssetPanel.vue`, `frontend/src/services/api.js` |
| Parsing packs, `gameType` dans le cfg | `backend/api/parsers/pack_parser.py`, `backend/api/parsers/editor_game_types.py`, `backend/editor/pack_meta.py` |
| Index statique packs | `scripts/generate_packs_index.py`, `scripts/backfill_cfg_game_type.py` |
| Cartes / users | `backend/editor/map_manager.py`, `backend/editor/user_manager.py`, `backend/api/views.py` |
| Config | `backend/zombicide_editor/settings.py`, `frontend/src/config.js` |
| Menu (masquage prod / dev) | `frontend/src/config/editorMenu.js` (`USE_MINIMAL_MENU`, `VITE_EDITOR_MINIMAL_MENU`) |

---

## Checklist de non-régression (interactions)

1. Drop depuis le panneau → élément créé **sélectionné**.
2. Clic sur élément → **sélection** (comportement attendu selon outil, sauf delete).
3. Pan → **grille + contenu** bougent ensemble (offset grille).
4. Zoom → grille et éléments **alignés**.
5. Outil **move** : déplacer, placer avec asset, pan sur fond vide.
6. Curseurs et halos (survol / sélection) **cohérents**.

---

*Dernière mise à jour : contexte figé à la demande pour le dépôt zproject.*
