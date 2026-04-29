# Informations de stockage

## Emplacement des cartes

Les cartes créées sont stockées dans :
```
media/users/<username>/maps/<map_id>.json
```

Par exemple :
- `media/users/temp/maps/map_abc123.json`
- `media/users/camp/maps/map_def456.json`

Le répertoire `media/` est défini dans `backend/zombicide_editor/settings.py` :
- `MEDIA_ROOT = BASE_DIR / 'media'`
- `USERS_DIR = MEDIA_ROOT / 'users'`

## Structure d'une carte

Chaque carte est un fichier JSON contenant :
- `id` : Identifiant unique de la carte
- `name` : Nom de la carte
- `pack` : Pack utilisé
- `grid` : Informations sur la grille (width, height, tileSize)
- `layers` : Couches de la carte (tiles, objects)
- `metadata` : Métadonnées (created, modified, author)
- `gridOffsetX`, `gridOffsetY` : Position de la grille

## Emplacement des assets

Les assets (packs Zombicide) sont stockés dans :
- `/assets/` : Nouveau répertoire unifié pour tous les packs
- `/bgmapeditor_tiles/` : Ancien répertoire (compatibilité)

Les packs uploadés via ZIP vont dans `/assets/`.
