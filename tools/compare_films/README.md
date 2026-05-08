# Comparaison de bibliothèques vidéo

**Copie de référence / travail à jour :** `D:\DEV\tools\compare_films\` — modifier le script et la doc là-bas ; ce dossier sous zproject peut rester en retard.

Script autonome (Python 3.9+) : compare le dossier du frère (`V:\FILMS - 2 To` par défaut, scan récursif) avec le vôtre (`Z:\FILMS` par défaut, racine + un niveau de sous-dossiers), puis génère un rapport HTML à quatre colonnes (Commun, Lui+, Moi+, HS suspects).

L’appariement combine une **clé normalisée** (comme avant) et un second passage **flou** sur les noms encore non appariés : tokens du titre (Dice), bonus si la **même année** apparaît dans les deux noms, et bonus si l’un des titres normalisés est une **sous-chaîne** de l’autre (ex. titres différents mais même film). Les paires floues sont marquées dans le HTML avec un badge « flou » et un score.

## Prérequis

- Python 3.9 ou plus récent (bibliothèque standard uniquement).
- Pour un scan direct des disques : lecteurs `V:` et `Z:` accessibles.

## Usage rapide (scan + HTML)

```bash
cd D:\DEV\tools\compare_films
python compare_films.py
```

Sans `--out`, un fichier `rapport_films_YYYYMMDD_HHMM.html` est créé dans le répertoire courant.

## Scan une fois, puis affiner sans toucher aux disques

1. **Exporter** deux fichiers liste (TSV UTF-8, extension `.txt`) :

```bash
python compare_films.py --export-only --out-brother films_frere.txt --out-mine films_moi.txt
```

2. **Régénérer le rapport** à partir des listes (ajuster `--fuzzy-threshold` entre 0 et 1, ex. `0.42` pour plus de matches, `0.55` pour être plus strict) :

```bash
python compare_films.py --brother-list films_frere.txt --mine-list films_moi.txt --fuzzy-threshold 0.48 --out rapport.html
```

## Options utiles

| Option | Description |
|--------|-------------|
| `--brother CHEMIN` | Racine côté frère (scan) |
| `--mine CHEMIN` | Racine côté vous (scan) |
| `--out rapport.html` | Fichier HTML de sortie |
| `--hs-mb 500` | Seuil en Mo pour la colonne « HS suspects » |
| `--fuzzy-threshold 0.48` | Seuil du score flou (0–1), défaut 0.48 |
| `--export-only` | N’écrit que les listes, pas de HTML |
| `--out-brother` / `--out-mine` | Noms des fichiers export (avec `--export-only`) |
| `--brother-list` / `--mine-list` | Listes en entrée pour le rapport sans rescan |
| `--no-recursive-brother` | Ne parcourir que le premier niveau du dossier frère |

## HS (suspects)

Les fichiers vidéo chez vous dont la taille est strictement inférieure au seuil (500 Mo par défaut) sont listés à part. C’est une heuristique (pas une analyse de contenu).
