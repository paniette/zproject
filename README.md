# Zombicide Scenario Editor - Application Web

Éditeur de cartes Zombicide compatible avec les packs du Mapeditor Windows.

## Fonctionnalités

- Import de packs ZIP compatibles avec Mapeditor Windows
- Éditeur de cartes avec drag & drop
- Placement de tuiles, portes, objets, spawn points, etc.
- Sauvegarde/chargement de cartes en JSON
- Export de cartes en image (PNG/JPEG)
- Système d'utilisateurs temporaires
- Upload de packs personnalisés (images individuelles ou ZIP complets)
- Détection automatique des nouveaux fichiers dans bgmapeditor_tiles/

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
├── bgmapeditor_tiles/    # Packs Zombicide (décompressés)
└── requirements.txt      # Dépendances Python
```

## Installation

### Backend (Django)

```bash
cd backend
pip install -r ../requirements.txt
python manage.py migrate  # Pas de migrations nécessaires (pas de BD)
python manage.py runserver
```

### Frontend (Vue.js)

```bash
cd frontend
npm install
npm run dev
```

L'application sera accessible sur http://localhost:5173

## Utilisation

1. Placez vos packs Zombicide dans le dossier `bgmapeditor_tiles/`
2. Lancez le serveur Django et le serveur de développement Vue
3. Ouvrez http://localhost:5173 dans votre navigateur
4. Sélectionnez un pack dans le panneau gauche
5. Glissez-déposez les assets sur le canvas pour créer votre carte
6. Sauvegardez avec Ctrl+S ou le bouton "Sauvegarder"
7. Exportez en image avec le bouton "Exporter"

## Technologies

- **Backend**: Django + Django REST Framework
- **Frontend**: Vue.js 3 + Vite + Pinia
- **Stockage**: Fichiers JSON (pas de base de données)
- **Images**: Pillow (PIL) pour traitement d'images
