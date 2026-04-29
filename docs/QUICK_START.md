# Démarrage rapide - Mode statique

## 1. Créer le fichier .env

Dans `frontend/`, créez un fichier `.env` avec :

```
VITE_STATIC_MODE=true
```

Ou copiez le template :
```bash
cd frontend
cp env.static .env
# Puis éditez .env et décommentez la ligne
```

## 2. Générer l'index des packs

```bash
cd scripts
python generate_packs_index.py
```

## 3. Tester en local

```bash
cd frontend
npm run dev
```

L'application fonctionne maintenant en mode statique :
- ✅ Packs chargés depuis `packs-index.json`
- ✅ Cartes sauvegardées dans localStorage
- ✅ Boutons d'upload désactivés

## 4. Build pour production

```bash
cd frontend
npm run build
```

Le build est dans `frontend/dist/` - prêt à être déployé sur Apache.

## Authentification Apache

Pour protéger `/editor/` avec un login/password :

1. **Générer le fichier .htpasswd** :
   ```bash
   python scripts/generate_htpasswd.py cyril cyril
   ```
   Copiez la ligne générée dans `/home/user/.htpasswd` (sur le serveur)

2. **Configurer .htaccess** :
   Modifiez le chemin dans `.htaccess` :
   ```apache
   AuthUserFile /home/user/.htpasswd
   ```

3. **Déployer** :
   - Uploader `frontend/dist/*` vers `/editor/` sur le serveur
   - Uploader `assets/` et `bgmapeditor_tiles/` à la racine
   - Uploader `.htaccess` à la racine

Voir `DEPLOYMENT.md` pour plus de détails.
