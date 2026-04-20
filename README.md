# Zombicide Scenario Editor - Application Web

Éditeur de cartes Zombicide compatible avec les packs du Mapeditor Windows.

Contexte technique détaillé (architecture, canvas, **mode statique sans Django**, fichiers pivots) : [`docs/CONTEXT.md`](docs/CONTEXT.md). Collaboration temps réel (hors périmètre court terme) : [`docs/COLLABORATION.md`](docs/COLLABORATION.md).

## Démarrage rapide (mode complet : frontend + backend)

En développement avec l’**API Django**, il faut **deux terminaux** ouverts en parallèle à la racine du dépôt (`zproject/`).

| Rôle | Répertoire | Commande | URL |
|------|--------------|----------|-----|
| **Frontend** (Vite + Vue) | `frontend/` | `npm install` une fois, puis `npm run dev` | [http://localhost:5173](http://localhost:5173) |
| **Backend** (Django) | `backend/` | `pip install -r ../requirements.txt` une fois, puis `python manage.py runserver` | [http://127.0.0.1:8000](http://127.0.0.1:8000) |

Le fichier [`frontend/vite.config.js`](frontend/vite.config.js) configure un **proxy** : depuis le port **5173**, les requêtes vers `/api` (et chemins médias utiles) sont envoyées vers **8000**. Ouvre l’éditeur dans le navigateur sur **5173** pour le mode complet.

Sous **Windows PowerShell**, enchaîne les commandes avec `;` si besoin, par exemple : `cd frontend; npm run dev`.

Pour le **mode statique** (sans Django), un seul `npm run dev` ou un build statique suffit ; voir [`docs/CONTEXT.md`](docs/CONTEXT.md) et [`README_STATIC.md`](README_STATIC.md).

## Fonctionnalités

### Carte & canvas

- Éditeur de cartes avec **drag & drop** depuis le panneau des assets
- Placement de tuiles, portes, objets, spawn points, etc. (selon le pack)
- **Grille**, **zoom**, **pan** ; outils Placer / Déplacer / Rotater / Supprimer
- **Onglet Mission** : métadonnées et texte de scénario liés à la carte (titre, objectifs, règles, capture carte pour la fiche mission, etc.)

### Édition & confort (Scenario Editor)

- **Annuler / Rétablir** (historique sur la carte : tuiles, objets, grille, mission) avec boutons et raccourcis **Ctrl+Z**, **Ctrl+Y**, **Ctrl+Shift+Z**
- **Panneau Propriétés** : position, rotation, `properties` (JSON) pour l’élément sélectionné
- **Mode Aperçu** : lecture seule sur le canvas (pan autorisé), barre d’outils désactivée visuellement
- Indicateur **Modifié / Enregistré** dans l’en-tête
- **Versions locales** : instantanés après une sauvegarde réussie, restauration depuis une modale (stockage `localStorage`)

### Exports & sauvegarde

- **Sauvegarde / chargement** des cartes en **JSON** (API Django ou mode statique via `localStorage`)
- **Export image** (PNG depuis le canvas, nom de fichier dérivé du nom de carte)
- **Export fichier JSON** du scénario (téléchargement)
- **Export XML** simplifié (interop / archivage)

### Packs & contenu

- Import de packs **ZIP** compatibles Mapeditor (nécessite le backend)
- **Utilisateurs temporaires** et sélection d’utilisateur pour les dossiers de cartes
- **Upload** d’assets personnalisés et de packs ZIP (masqué en mode statique)
- Détection / indexation des packs (y compris répertoires type `bgmapeditor_tiles/` ou médias Django)

### Interface

- **Thèmes** d’interface (liste déroulante, persistance, variables CSS)
- Libellés et tooltips **Utilisateur** / **Thème** pour clarifier l’UI

### Mode statique (sans Django)

- Avec **`VITE_STATIC_MODE`** non défini ou ≠ `false` au build, l’app utilise des **index JSON** et le **navigateur** pour packs et cartes — pas besoin de `runserver`. Voir [`docs/CONTEXT.md`](docs/CONTEXT.md) section *Mode statique*.

### Menu allégé en production

- Fichier [`frontend/src/config/editorMenu.js`](frontend/src/config/editorMenu.js) : flags par bouton (JSON, XML, Versions, Thème, Utilisateur, uploads) ou **`USE_MINIMAL_MENU`** / variable **`VITE_EDITOR_MINIMAL_MENU=true`** au build pour tout masquer d’un coup (hors onglets Carte/Mission, outils, aperçu, chargement/sauvegarde icônes, export image).

## Structure du Projet

```
.
├── backend/              # Django backend
│   ├── zombicide_editor/ # Configuration Django
│   ├── api/              # API REST
│   ├── editor/           # Logique métier (maps, users, packs)
│   └── manage.py
├── frontend/             # Vue.js frontend
│   ├── src/
│   │   ├── components/   # Composants Vue
│   │   ├── stores/       # Stores Pinia
│   │   ├── services/     # Services API
│   │   └── utils/        # Utilitaires
│   └── package.json
├── docs/                 # CONTEXT, COLLABORATION, etc.
├── bgmapeditor_tiles/    # Packs Zombicide (décompressés)
└── requirements.txt      # Dépendances Python
```

## Installation (première fois)

### Backend (Django)

```bash
cd backend
pip install -r ../requirements.txt
python manage.py migrate  # si nécessaire selon ton environnement
python manage.py runserver
```

Le serveur API écoute par défaut sur **http://127.0.0.1:8000**.

### Frontend (Vue.js)

```bash
cd frontend
npm install
npm run dev
```

L’interface de développement est sur **http://localhost:5173** (avec proxy vers l’API si le backend tourne, voir section *Démarrage rapide* ci-dessus).

## Utilisation

1. Placez vos packs Zombicide dans le dossier `bgmapeditor_tiles/` (ou selon votre config médias)
2. Pour le mode **complet** : lancez Django et le serveur de dev Vite ; ouvrez http://localhost:5173
3. Pour le mode **statique** : build ou hébergement des fichiers générés + `packs-index.json` / `maps-index.json` si besoin
4. Sélectionnez un pack dans le panneau gauche
5. Glissez-déposez les assets sur le canvas pour créer votre carte
6. Sauvegardez avec **Ctrl+S** ou le bouton « Sauvegarder » ; utilisez **Annuler / Rétablir** si besoin
7. Exportez en **image**, **JSON** ou **XML** selon les boutons de l’en-tête

## Technologies

- **Backend**: Django + Django REST Framework
- **Frontend**: Vue.js 3 + Vite + Pinia
- **Stockage**: Fichiers JSON (pas de base de données métier)
- **Images**: Pillow (PIL) pour traitement d’images côté serveur
