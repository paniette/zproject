# Build statique avec pré-indexation

Ce guide explique comment générer un build statique de l'application qui fonctionne sans serveur Django.

## Prérequis

- Python 3.8+ avec Django installé (uniquement pour générer l'index)
- Node.js et npm (pour le build frontend)

## Étapes

### 1. Générer l'index des packs

Exécutez le script Python pour générer le fichier `packs-index.json` :

```bash
cd scripts
python generate_packs_index.py
```

Ce script va :
- Scanner les dossiers `/assets/` et `/bgmapeditor_tiles/`
- Parser tous les fichiers `.cfg` pour découvrir les packs
- Indexer tous les assets (images, rotations, thumbnails)
- Générer un fichier JSON dans `frontend/public/packs-index.json`

### 2. Copier les assets

Assurez-vous que les dossiers d'assets sont accessibles :
- `/assets/` doit être copié dans le répertoire de build
- `/bgmapeditor_tiles/` doit être copié dans le répertoire de build (si utilisé)

### 3. Configurer le mode statique

Créez un fichier `.env` dans `frontend/` :

```bash
cd frontend
cp .env.example .env
```

Modifiez `.env` pour activer le mode statique :

```
VITE_STATIC_MODE=true
```

### 4. Build du frontend

```bash
cd frontend
npm run build
```

Le build sera généré dans `frontend/dist/`.

### 5. Déployer

Copiez le contenu de `frontend/dist/` sur votre serveur web statique, ainsi que :
- Le dossier `/assets/` (ou configurez votre serveur pour servir ce dossier)
- Le dossier `/bgmapeditor_tiles/` (si utilisé)

## Fonctionnalités en mode statique

✅ **Fonctionnel :**
- Affichage des packs et assets
- Édition de cartes
- Sauvegarde/chargement de cartes (localStorage)
- Export de cartes en image

❌ **Désactivé :**
- Upload de packs ZIP
- Upload d'éléments individuels
- Sauvegarde serveur (utilise localStorage à la place)

## Structure des fichiers

```
frontend/
  dist/                    # Build de production
    index.html
    assets/
    packs-index.json       # Index généré
  public/
    packs-index.json       # Index source (copié dans dist/)
  .env                     # Configuration (VITE_STATIC_MODE=true)
```

## Notes

- Les cartes sont sauvegardées dans le localStorage du navigateur
- Chaque utilisateur a ses propres cartes (basé sur le nom d'utilisateur)
- Pour mettre à jour les packs, régénérez `packs-index.json` et rebuild
- La taille du localStorage est limitée (~5-10MB selon le navigateur)
