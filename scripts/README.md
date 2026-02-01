# Scripts utilitaires

## generate_packs_index.py

Génère un fichier JSON statique avec tous les packs et leurs assets indexés.

### Utilisation

```bash
cd scripts
python generate_packs_index.py
```

### Prérequis

- Python 3.8+
- Django et les dépendances installées (voir `requirements.txt`)
- Les dossiers `/assets/` et `/bgmapeditor_tiles/` doivent exister

### Sortie

Le script génère `frontend/public/packs-index.json` qui contient :
- Liste de tous les packs
- Pour chaque pack : tous les assets organisés par catégorie
- Métadonnées (noms, images, alignements)

### Format du fichier généré

```json
{
  "packs": [
    {
      "id": "G-Zombicide-A6-ZC",
      "name": "Zombicide A6",
      "image": "assets/G-Zombicide-A6-ZC/...",
      "align": 25,
      "assets": {
        "01.tiles": [
          {
            "name": "10V",
            "path": "assets/G-Zombicide-A6-ZC/01.tiles/10V.png",
            "thumbnail": "assets/G-Zombicide-A6-ZC/01.tiles/10V.png/r_thumb.png",
            "rotations": [...]
          }
        ],
        ...
      }
    }
  ],
  "generated_at": "2024-01-01T12:00:00"
}
```
