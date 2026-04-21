---
name: zproject-prep-static-ftp
description: >-
  Génère les JSON statiques (packs-index, maps-index, copies des cartes) pour déploiement FTP ; décrit le basculement VITE_STATIC_MODE dans frontend/.env autour d’un npm run build.
  À appliquer lorsque l’utilisateur demande de préparer la migration vers le FTP en mode statique, préparer les fichiers statiques pour le FTP,
  régénérer packs-index/maps-index pour le statique, build statique pour FTP, ou toute formulation équivalente.
---

# Préparer les artefacts statiques FTP (zproject)

## Quand appliquer cette skill

- **« Prépare la migration vers mon/mes FTP en statique »**, **« prépare le déploiement statique »**, **« régénère les JSON pour le mode statique »**, etc.
- Par défaut : **uniquement** les scripts Python (pas de `npm run build`), sauf si l’utilisateur demande **explicitement** un build pour le FTP.

## Comportement attendu — scripts JSON (sans build)

1. Depuis la **racine du workspace** (`zproject`), exécuter (PowerShell : `;` si besoin) :
   - `cd scripts`
   - `python generate_packs_index.py`
   - `python generate_maps_index.py`  
   Sur Windows, utiliser `py` à la place de `python` si nécessaire.

2. **Prérequis** : venv + `pip install -r requirements.txt` si besoin. Django via `DJANGO_SETTINGS_MODULE=zombicide_editor.settings`.

## Comportement attendu — `npm run build` pour un déploiement statique en ligne

Pour que le bundle utilise **packs-index / cartes statiques** (et pas l’API Django), **`VITE_STATIC_MODE` doit être `true` au moment du build**. En local, après le build, il faut **revenir à `false`** pour retrouver le mode dev avec Django (packs et assets via l’API).

**Workflow obligatoire** (fichier **`frontend/.env`**) :

1. **Avant** `npm run build` : mettre  
   `VITE_STATIC_MODE=true`  
   (sauvegarder le fichier.)
2. Lancer le build : `cd frontend` puis `npm run build`.
3. **Juste après** le build : remettre  
   `VITE_STATIC_MODE=false`  
   pour le travail quotidien en local.

Sans l’étape 1, un build avec `false` produit une app qui attend l’API : **en ligne sur FTP sans Django**, les packs et assets ne se chargent pas correctement. Sans l’étape 3, le dev local reste coincé en mode statique.

## Fichiers produits par les scripts (à uploader / fusionner sur le FTP)

Sous **`frontend/public/`** :

| Fichier / dossier | Rôle |
|-------------------|------|
| `packs-index.json` | Index des packs pour le mode statique |
| `maps-index.json` | Index des cartes (métadonnées + liste) |
| `maps/*.json` | Une copie par carte (corps complet du scénario) |

À copier sur le FTP aux **mêmes chemins relatifs** qu’à la racine du site généré par Vite (`dist/`), en plus du contenu du **`dist/`** si tu fais un build statique.

## Rappels utiles

- Les cartes visibles pour l’utilisateur **temp** en statique : `metadata.author === "temp"` dans chaque JSON (`frontend/src/services/api.js`).
- Tuiles / médias : toujours déployer **`assets/`**, **`bgmapeditor_tiles/`** (ou chemins prévus par ton `packs-index`) selon le README statique du projet.

## En cas d’erreur

- Django / imports : venv, `requirements.txt`, exécution depuis `scripts/`.
- Index de cartes vide : vérifier `media/users/*/maps/*.json` (`MEDIA_ROOT` / `USERS_DIR` dans `backend/zombicide_editor/settings.py`).
