---
name: zproject-allume
description: >-
  Démarre le serveur de dev Vue/Vite (frontend) et Django (backend) du projet zproject.
  À appliquer lorsque l’utilisateur dit allume le projet, démarre le projet, lance le projet,
  démarre zproject, ou demande explicitement les deux serveurs (npm run dev + runserver).
---

# Allumer le projet zproject

## Quand appliquer cette skill

- Formulations du type : **« allume le projet »**, **« démarre le projet »**, **« lance le projet »**, **« lance le front et le back »**, **« démarre zproject »**, etc., pour ce dépôt (éditeur Zombicide / `zproject`).

## Comportement attendu

1. **Vérifier** dans le dossier `terminals` du workspace s’il existe déjà une session avec `npm run dev` ou `runserver` actif ; si oui, l’indiquer plutôt que dupliquer sans raison.
2. **Démarrer le frontend** (processus long) :
   - Répertoire de travail : `frontend/` (relatif à la racine du workspace, ex. `d:\DEV\zproject\frontend`).
   - Commande : `npm run dev`
   - Utiliser un **lancement en arrière-plan** (ne pas bloquer l’agent sur le serveur Vite).
3. **Démarrer le backend** (processus long) :
   - Répertoire de travail : `backend/`
   - Commande : `python manage.py runserver` (sur Windows, utiliser `py manage.py runserver` si `python` n’est pas dans le PATH).
   - **Arrière-plan** également.
4. **Informer l’utilisateur** des URL habituelles :
   - Frontend : `http://localhost:5173`
   - API Django : `http://127.0.0.1:8000` (le proxy Vite du frontend pointe `/api` vers ce serveur en dev).
5. **Ensuite** : poursuivre le reste de la demande utilisateur (vérification, autre tâche, etc.) — ne pas considérer que la conversation s’arrête après le démarrage des serveurs.

## Prérequis (si échec au lancement)

- Frontend : `npm install` dans `frontend/` si les modules manquent.
- Backend : depuis `backend/`, `pip install -r ../requirements.txt` (voir `README.md` du repo). Migrations : `python manage.py migrate` si nécessaire.

## Shell Windows (PowerShell)

Enchaîner avec `;` plutôt que `&&` si besoin : `cd frontend; npm run dev`.
