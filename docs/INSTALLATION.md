# Installation des dépendances

## Backend (Django)

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
- Django==5.0.1
- djangorestframework==3.14.0
- django-cors-headers==4.3.1
- Pillow==10.0.0 (pour le traitement d'images)
- watchdog==3.0.0 (pour la surveillance des fichiers)

## Démarrer le serveur Django

```bash
cd backend
python manage.py runserver
```

Le serveur sera accessible sur `http://localhost:8000`

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

1. Vérifiez que le serveur Django est démarré
2. Vérifiez que les dépendances sont installées : `pip list | grep Django`
3. Vérifiez que CORS est configuré correctement dans `settings.py`
4. Le CSRF est désactivé pour les vues d'upload (via `@method_decorator(csrf_exempt)`)
