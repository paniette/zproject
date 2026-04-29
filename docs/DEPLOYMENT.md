# Guide de déploiement Apache avec authentification

## Prérequis

- Serveur Apache avec mod_rewrite et mod_auth_basic activés
- Accès SSH au serveur
- Git installé

## Étapes de déploiement

### 1. Générer l'index des packs (en local)

```bash
cd scripts
python generate_packs_index.py
```

Cela génère `frontend/public/packs-index.json`

### 2. Build du frontend

```bash
cd frontend
npm run build
```

Le build est dans `frontend/dist/`

### 3. Créer le fichier .htpasswd

Sur le serveur, générez le fichier `.htpasswd` :

```bash
# Option 1: Avec htpasswd (Apache)
htpasswd -c /home/user/.htpasswd cyril
# Entrez le mot de passe: cyril

# Option 2: Avec Python
python3 -c "import crypt; print('cyril:' + crypt.crypt('cyril', crypt.mksalt(crypt.METHOD_MD5)))" > /home/user/.htpasswd

# Option 3: En ligne
# Visitez https://hostingcanada.org/htpasswd-generator/
# Username: cyril, Password: cyril
# Copiez le résultat dans /home/user/.htpasswd
```

**Important** : Placez le fichier `.htpasswd` **EN DEHORS** du répertoire web pour la sécurité !

### 4. Configurer les permissions

```bash
chmod 644 /home/user/.htpasswd
chown www-data:www-data /home/user/.htpasswd  # ou apache:apache selon votre système
```

### 5. Déployer sur le serveur

#### Option A: Via Git

```bash
# Sur le serveur
cd /var/www/html  # ou votre répertoire web
git clone https://github.com/votre-repo/zombicide-editor.git
cd zombicide-editor

# Copier le build
cp -r frontend/dist/* /var/www/html/editor/

# Copier les assets
cp -r assets /var/www/html/
cp -r bgmapeditor_tiles /var/www/html/  # si utilisé
```

#### Option B: Via FTP/SFTP

1. Uploader le contenu de `frontend/dist/` vers `/editor/` sur le serveur
2. Uploader les dossiers `assets/` et `bgmapeditor_tiles/` à la racine
3. Uploader `.htaccess` à la racine (ou dans `/editor/`)

### 6. Configurer Apache

#### Configuration dans .htaccess (à la racine)

Modifiez le chemin dans `.htaccess` :

```apache
AuthUserFile /home/user/.htpasswd
```

Remplacez `/home/user/.htpasswd` par le chemin réel de votre fichier `.htpasswd`.

#### Configuration dans httpd.conf (alternative)

Si vous préférez configurer dans le VirtualHost :

```apache
<VirtualHost *:80>
    ServerName votre-domaine.com
    DocumentRoot /var/www/html
    
    <Directory /var/www/html/editor>
        AuthType Basic
        AuthName "Zombicide Editor - Accès Restreint"
        AuthUserFile /home/user/.htpasswd
        Require valid-user
        
        # Allow static files
        <FilesMatch "\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot|json)$">
            Require all granted
        </FilesMatch>
    </Directory>
    
    # Serve assets without auth
    Alias /assets /var/www/html/assets
    <Directory /var/www/html/assets>
        Require all granted
    </Directory>
</VirtualHost>
```

### 7. Structure finale sur le serveur

```
/var/www/html/
├── index.html              # Landing page
├── css/
├── js/
├── .htaccess              # Configuration Apache
├── editor/                # Application Vue.js (protégée)
│   ├── index.html
│   ├── assets/
│   └── packs-index.json
├── assets/                # Packs Zombicide (public)
│   └── G-Zombicide-...
└── bgmapeditor_tiles/     # Packs legacy (public, optionnel)
```

### 8. Tester

1. Visitez `http://votre-domaine.com` → Landing page (publique)
2. Cliquez sur "En savoir plus" → Redirige vers `/editor/`
3. Une popup d'authentification apparaît
4. Entrez : `cyril` / `cyril`
5. L'éditeur se charge

## Sécurité

- ✅ `.htpasswd` est en dehors du répertoire web
- ✅ Les assets (images) sont accessibles sans auth
- ✅ Seul `/editor/` est protégé
- ❌ Ne commitez JAMAIS `.htpasswd` dans Git
- ✅ Ajoutez `.htpasswd` au `.gitignore`

## Mise à jour

Pour mettre à jour l'application :

```bash
# Sur le serveur
cd /var/www/html/zombicide-editor
git pull
cd frontend
npm run build
cp -r dist/* /var/www/html/editor/
```

## Dépannage

### L'authentification ne fonctionne pas

1. Vérifiez que `mod_auth_basic` est activé : `a2enmod auth_basic`
2. Vérifiez le chemin de `.htpasswd` dans `.htaccess`
3. Vérifiez les permissions : `ls -la /home/user/.htpasswd`
4. Vérifiez les logs Apache : `tail -f /var/log/apache2/error.log`

### Les assets ne se chargent pas

1. Vérifiez que les dossiers `assets/` et `bgmapeditor_tiles/` sont accessibles
2. Vérifiez les permissions : `chmod -R 755 /var/www/html/assets`
3. Vérifiez la configuration CORS dans `.htaccess`

### Le routing SPA ne fonctionne pas

1. Vérifiez que `mod_rewrite` est activé : `a2enmod rewrite`
2. Vérifiez que `.htaccess` est lu : `AllowOverride All` dans httpd.conf
