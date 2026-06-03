# Couleurs mission par thème — zproject

Variables CSS de couleur pour le rendu A4 (`mission-print.css` + `MissionPagePreview.vue`).  
Référence visuelle cible : PDFs officiels CMON + template communautaire [All Zombicides (Figma)](https://www.figma.com/design/yT1dVj59QjU7jrCX7Kk5v3/All-Zombicides).

Fantasy conserve ses valeurs calibrées séparément — voir bloc `[data-mission-theme='fantasy']` dans `mission-print.css`.

---

## Variables

| Variable | Rôle | Éléments HTML |
|----------|------|---------------|
| `--mp-bg` | Fond page A4 | `.mp-sheet`, `@media print` |
| `--mp-ink` | Texte corps / titres par défaut | `.mp-title`, `.mp-list`, `.mp-meta-line`… |
| `--mp-quest` | Code mission (WM44, C55…) | `.mp-quest-code` |
| `--mp-heading` | Titres de section | `.mp-section-title`, `.mp-aside-title` |
| `--mp-accent` | Accents (titres classic/night, bordures tuiles) | overrides thème |
| `--mp-dropcap` | Première lettre synopsis | `.mp-synopsis--dropcap::first-letter` |
| `--mp-vignette` | Fondu bords feuille | `.mp-sheet` box-shadow inset |
| `--mp-token-bg` | Fond encart jetons | `.mp-token-summary` |

---

## Modern (Zombicide 2nd Edition)

Monochrome noir sur gris clair neutre (réf. WM44).

| Variable | Hex / rgba | Source |
|----------|------------|--------|
| `--mp-bg` | `#EBEBEB` | PDF 2E — fond gris clair |
| `--mp-ink` | `#000000` | PDF 2E — corps |
| `--mp-quest` | `#000000` | PDF 2E — code mission condensed |
| `--mp-heading` | `#000000` | PDF 2E — titres section |
| `--mp-accent` | `#000000` | PDF 2E — peu d’accent couleur |
| `--mp-dropcap` | `#000000` | Synopsis Gorri Sans |
| `--mp-vignette` | `rgba(0, 0, 0, 0.18)` | Léger fondu |
| `--mp-token-bg` | `#C8C8C8` | Encart matériel gris taupe |

---

## Classic (1ère édition)

Parchemin chaud + rouge brand Zombicide.

| Variable | Hex / rgba | Source |
|----------|------------|--------|
| `--mp-bg` | `#EEDAB7` | Template Classic / parchemin |
| `--mp-ink` | `#000000` | Corps noir |
| `--mp-quest` | `#C41230` | Rouge brand |
| `--mp-heading` | `#000000` | Titres section |
| `--mp-accent` | `#C41230` | Titres Creepster / branding |
| `--mp-dropcap` | `#C41230` | Dropcap rouge |
| `--mp-vignette` | `rgba(80, 40, 10, 0.22)` | Fondu chaud marron |
| `--mp-token-bg` | `#D4C4A8` | Encart beige parchemin |

---

## Western (Undead or Alive)

Sable / affiche wanted, bruns et rouille.

| Variable | Hex / rgba | Source |
|----------|------------|--------|
| `--mp-bg` | `#F5E6C8` | Template UoA — sable |
| `--mp-ink` | `#2B1810` | Encre brun foncé |
| `--mp-quest` | `#5C3A18` | Brun selle (codes) |
| `--mp-heading` | `#9A4B0F` | Rouille / titres section |
| `--mp-accent` | `#9A4B0F` | Accents western |
| `--mp-dropcap` | `#8B4513` | Dropcap brun chaud |
| `--mp-vignette` | `rgba(90, 50, 10, 0.25)` | Fondu sienna |
| `--mp-token-bg` | `#C9A87C` | Encart tan |

---

## Sci-Fi (Invader / Dark Side)

Gris froid + cyan Invader.

| Variable | Hex / rgba | Source |
|----------|------------|--------|
| `--mp-bg` | `#E8ECF0` | Template Sci-Fi — gris froid clair |
| `--mp-ink` | `#0D1117` | Presque noir bleuté |
| `--mp-quest` | `#0099CC` | Cyan codes mission |
| `--mp-heading` | `#0D1117` | Titres Zekton |
| `--mp-accent` | `#0099CC` | Accent cyan |
| `--mp-dropcap` | `#1A1F2E` | Corps synopsis |
| `--mp-vignette` | `rgba(10, 20, 40, 0.20)` | Fondu bleu froid |
| `--mp-token-bg` | `#B0BEC5` | Encart métal froid |

---

## Night / NOTLD

Esthétique Romero N&B — papier crème, encre noire (pas de vert UI).

| Variable | Hex / rgba | Source |
|----------|------------|--------|
| `--mp-bg` | `#F5F0E6` | Papier crème / blanc cassé |
| `--mp-ink` | `#000000` | Encre noire |
| `--mp-quest` | `#000000` | Code Anton impact |
| `--mp-heading` | `#000000` | Titres section |
| `--mp-accent` | `#000000` | Accents (monochrome) |
| `--mp-dropcap` | `#000000` | Dropcap |
| `--mp-vignette` | `rgba(0, 0, 0, 0.15)` | Fondu discret film |
| `--mp-token-bg` | `#D9D9D9` | Encart gris clair |

---

## Fantasy (référence — inchangé)

| Variable | Hex / rgba | Notes |
|----------|------------|-------|
| `--mp-bg` | `#f1efe2` | Parchemin médiéval |
| `--mp-ink` | `#000000` | |
| `--mp-quest` | `#196aa9` | Bleu code quête |
| `--mp-heading` | `#573c27` | Marron titres gothiques |
| `--mp-accent` | `#7d1618` | Bordeaux |
| `--mp-dropcap` | `#c1212b` | Rouge dropcap |
| `--mp-vignette` | `rgba(68, 32, 6, 0.32)` | |
| `--mp-token-bg` | `#bfab9a` | Encart taupe (mini-grille tuiles aussi) |

---

## Affinage Figma

Les hex ci-dessus sont une première passe alignée PDF + analyse visuelle. Pour affiner :

1. Ouvrir [All-Zombicides](https://www.figma.com/design/yT1dVj59QjU7jrCX7Kk5v3/All-Zombicides) → page du thème concerné
2. Pipette sur le calque **Background**, textes **Quest / Title / Section / Body**, encart **Tokens**
3. Mettre à jour les blocs `[data-mission-theme='…']` dans `frontend/src/assets/mission-print.css`
