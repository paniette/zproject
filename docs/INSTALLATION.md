# Installation des dépendances

## Backend (FastAPI)

Pour installer les dépendances Python, exécutez :

```bash
cd backend
pip install -r ../requirements.txt
```

Ou si vous utilisez un environnement virtuel :

```bash
cd backend
python -m venv venv
# Sur Windows:
venv\Scripts\activate
# Sur Linux/Mac:
source venv/bin/activate

pip install -r ../requirements.txt
```

## Dépendances requises

Les dépendances sont listées dans `requirements.txt` :

- fastapi, uvicorn (serveur ASGI)
- python-multipart (formulaires / uploads)
- Pillow (traitement d’images)
- watchdog (surveillance des fichiers, optionnel pour le watcher)

## Démarrer le serveur API

```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Le serveur sera accessible sur `http://127.0.0.1:8000` (le proxy Vite du frontend pointe vers ce port).

## Frontend (Vue.js)

Pour installer les dépendances Node.js :

```bash
cd frontend
npm install
```

## Démarrer le serveur de développement

```bash
cd frontend
npm run dev
```

Le frontend sera accessible sur `http://localhost:5173`

## Résolution de l'erreur 405

Si vous obtenez une erreur 405 (Method Not Allowed) lors de l'upload :

1. Vérifiez que le serveur FastAPI est démarré (`uvicorn` sur le port 8000)
2. Vérifiez que les dépendances sont installées : `pip show fastapi`
3. Vérifiez que CORS est configuré dans `backend/app_config.py` (origines alignées avec Vite)
