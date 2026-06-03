# Contexte projet — zproject

Document **court** pour reprendre le dev (humains et agents). Détails par domaine : annexes ci-dessous. Démarrage local et stack : [`README.md`](../README.md).

---

## Objectif

Éditeur web de **scénarios Zombicide** : carte interactive (Mapeditor) + **fiche mission** imprimable (style PDF officiel) avec **capture de la carte** en bas. Persistance **JSON**, pas de BDD. Production cible : **mode statique** sans Python (`z.paniette.fr`).

**Tâches** : « tâche N » / « issue #N » → [issue GitHub](https://github.com/paniette/zproject/issues/N) (pas de liste locale). Détail : règle `.cursor/rules/github-issues.mdc`.

---

## Vocabulaire

| Terme (utilisateur) | Code / UI | Rôle |
|----------------------|-----------|------|
| **Page carte**, map, plans | `#/` · `MapEditor` | Édition canvas : `layers.tiles` / `layers.objects` — **source géométrique**. |
| **Page mission** | `#/mission` · `MissionEditor` | Rendu **HTML A4** (`MissionPagePreview`) + `@media print` — **pas** un éditeur PDF séparé. |
| **Capture carte** | `mission.mapImageDataUrl` | PNG sans grille (crop auto) via `canvasExport.js` → `CanvasGrid`. |
| **Mode statique** | `config.staticMode` | Packs/cartes sans FastAPI : index JSON + `localStorage`. |

**Ne pas confondre** : canvas interactif ≠ PNG mission · thème UI (`themeStore` / `data-theme`) ≠ thème fiche (`mission.pageTheme` / `#mission-print-root`).

**Architecture** : une SPA, deux onglets (`EditorLayout`, `v-show`), **un seul store** `mapStore` (carte + `mission` + undo/redo). **Ne pas** créer de `missionStore` séparé. Router hash : `#/`, `#/mission`.

Schéma mission : [`frontend/src/utils/mission.js`](../frontend/src/utils/mission.js). Utilisateur par défaut : **`temp`** (`userStore`).

---

## Trois « thèmes » liés

| Concept | Où | Rôle |
|---------|-----|------|
| **`mission.pageTheme`** | JSON mission | Style **PDF mission** (classic, modern, fantasy, western, scifi, night). |
| **`pack.gameType`** | `cfg` pack / `packs-index.json` | Série du **pack** ; filtre panneau Packs & Assets. |
| **`themeStore.activeTheme`** | UI éditeur | Thème chrome + filtre assets ; en Mission, sync vers `pageTheme` via `setTheme`. |

Détail mission : [`CONTEXT_MISSION.md`](CONTEXT_MISSION.md). Détail packs : [`CONTEXT_PACKS.md`](CONTEXT_PACKS.md).

---

## Décisions produit (figées)

| Sujet | Décision |
|-------|----------|
| Style page mission | Reproduire le **PDF officiel** de chaque `pageTheme` (affinage continu). |
| Capture / export PNG | **Crop auto** tuiles posées — même pipeline que l’export en-tête (`mapExportBounds.js`). |
| Format mission | **Une page A4** (pas de multi-pages court terme). |
| Utilisateur | **`temp`** (dev + statique longtemps) ; cartes embarquées `metadata.author === "temp"`. |
| PDF | **100 % client** (`window.print()`). |

---

## Mode statique (impératif)

Prod sans FastAPI. Dev local **avec** API : `frontend/.env` → `VITE_STATIC_MODE=false`. Build FTP : `true` avant `npm run build`, puis remettre `false` (skill `zproject-prep-static-ftp`).

| Fichier | Rôle |
|---------|------|
| `frontend/src/config.js` | `staticMode` (défaut **activé** sauf `'false'` au build). |
| `frontend/src/services/api.js` | **Seule façade** HTTP : `fetch` index + `localStorage` si statique. |
| `frontend/public/packs-index.json`, `maps-index.json`, `maps/*.json` | Données embarquées. |
| `scripts/generate_packs_index.py`, `generate_maps_index.py` | Régénération index. |

**Règles** : jamais `/api/...` depuis un composant · tester statique **et** API · feature backend-only → UI masquée ou i18n · médias via `api.getAsset()` · nouveaux champs JSON → localStorage + scripts maps si besoin.

**Pièges** : capture carte depuis onglet Mission (`CanvasGrid` en `v-show`, doit exporter quand même) · proxy Vite 5173→8000 uniquement en dev API · chemins packs : `bgmapeditor_tiles/`, `assets/`, ou `backend/media/` selon config.

Guide déploiement : [`README_STATIC.md`](README_STATIC.md).

---

## Chemins & docs (quand lire quoi)

| Besoin | Document |
|--------|----------|
| Contexte général (ce fichier) | `docs/CONTEXT.md` |
| Canvas, pan, zoom, outils | [`CONTEXT_CANVAS.md`](CONTEXT_CANVAS.md) |
| Page mission, print, layout | [`CONTEXT_MISSION.md`](CONTEXT_MISSION.md) |
| Packs Mapeditor, `gameType`, index | [`CONTEXT_PACKS.md`](CONTEXT_PACKS.md) |
| API FastAPI, modules Python | [`BACKEND_REFERENCE.md`](BACKEND_REFERENCE.md) |
| Install, démarrage, features | [`README.md`](../README.md) |
| Build / FTP statique | [`README_STATIC.md`](README_STATIC.md), [`STATIC_BUILD.md`](STATIC_BUILD.md) |
| Collaboration (hors scope) | [`COLLABORATION.md`](COLLABORATION.md) |

**Menu prod** : `frontend/src/config/editorMenu.js` — `USE_MINIMAL_MENU` / `VITE_EDITOR_MINIMAL_MENU` masque exports, uploads, thème, etc. ; uploads aussi off si `staticMode`.

**i18n** : tout texte UI via `$t` / `t` ; 4 locales (`fr`, `en`, `de`, `es`). Asset labels : `assetDictionary.js`.

---

## Fichiers pivots

| Sujet | Fichiers |
|-------|----------|
| Layout onglets | `EditorLayout.vue`, `router/index.js`, `AppHeader.vue` |
| État scénario | `stores/mapStore.js`, `utils/mission.js` |
| Page carte | `MapEditor.vue`, `CanvasGrid.vue`, `canvasRenderer.js`, `stores/toolStore.js` |
| Page mission | `MissionEditor.vue`, `MissionPagePreview.vue`, `assets/mission-print.css` |
| Capture PNG | `services/canvasExport.js`, `utils/mapExportBounds.js`, `CanvasGrid.vue` |
| API / statique | `services/api.js`, `services/localStorage.js`, `config.js` |
| Thèmes | `stores/themeStore.js`, `config/missionCornerImages.js`, `config/tokenSummary.js` |
| Packs (backend) | `backend/api/parsers/pack_parser.py`, `backend/routes/packs.py` |
| Menu / prod | `config/editorMenu.js` |

---

## Anti-patterns

- Appeler l’API hors `api.js`.
- Hardcoder des chaînes UI (sans i18n).
- Dupliquer l’état mission hors `mapStore`.
- Casser le mode statique pour une feature « dev only ».
- Exporter toute la grille vide (ignorer `mapExportBounds`).

---

*Juin 2026 — contexte principal allégé ; annexes `CONTEXT_*.md`.*
