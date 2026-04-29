# Mode Statique - Guide rapide

## Activation du mode statique

1. **Générer l'index des packs** (nécessite Python/Django) :
   ```bash
   cd scripts
   python generate_packs_index.py
   ```
   Cela génère `frontend/public/packs-index.json`

2. **Activer le mode statique** :
   Créez `frontend/.env` avec :
   ```
   VITE_STATIC_MODE=true
   ```

3. **Build** :
   ```bash
   cd frontend
   npm run build
   ```

## Fonctionnalités

✅ **Mode statique activé :**
- Packs chargés depuis `packs-index.json`
- Cartes sauvegardées dans localStorage
- Boutons d'upload désactivés

✅ **Mode normal (VITE_STATIC_MODE=false) :**
- Packs chargés depuis l'API Django
- Cartes sauvegardées sur le serveur
- Boutons d'upload actifs

## Déploiement statique

1. Build : `npm run build`
2. Copier `frontend/dist/` sur votre serveur web
3. Copier `/assets/` et `/bgmapeditor_tiles/` sur le serveur
4. Configurer le serveur pour servir ces dossiers

Les cartes sont stockées dans le localStorage du navigateur (par utilisateur).

## Cartes « serveur » (liste Charger) + cartes créées en local

- **Liste « Charger une carte »** : fusion de `maps-index.json` + les entrées `localStorage` pour l’utilisateur courant (par défaut `temp`). Seules les cartes dont `metadata.author` correspond à l’utilisateur sélectionné apparaissent.
- **Publier des cartes faites en dev Django** : copier les JSON depuis `media/users/<user>/maps/*.json` (ou équivalent) vers `frontend/public/maps/`, puis depuis la racine du dépôt exécuter `cd scripts` et `python generate_maps_index.py` (met à jour `frontend/public/maps-index.json` et recopie les fichiers). Rebuild (`npm run build` avec `VITE_STATIC_MODE=true`) et déployer `dist/` + `maps/` + `maps-index.json`.
- **Supprimer** : une carte entièrement dans le `localStorage` est effacée pour de bon. Une carte qui vient seulement des fichiers statiques ne peut pas être supprimée sur le disque du FTP ; le bouton supprime l’entrée **pour ce navigateur** (liste masquée dans `localStorage`, clé `zombicide_static_maps_suppressed`).
