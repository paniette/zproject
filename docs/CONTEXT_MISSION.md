# Annexe — Page mission (fiche A4)

Rendu imprimable, capture carte, mise en page adaptative. Retour : [`CONTEXT.md`](CONTEXT.md).

---

## Composants

| Fichier | Rôle |
|---------|------|
| `MissionEditor.vue` | Formulaire champs + capture / print / sync tuiles. |
| `MissionPagePreview.vue` | Rendu A4 live ; `#mission-print-root`. |
| `assets/mission-fonts.css` | `@font-face` pour les 5 thèmes + fallbacks Fantasy — polices auto-hébergées. |
| `assets/mission-print.css` | Variables par `data-mission-theme` (dont `--mp-font-*`), `@media print`. |
| `utils/mission.js` | `defaultMission()`, `mergeMissionFromPayload`, `deriveTilesFromLayers`. |
| `config/missionCornerImages.js` | Décor coin par série. |
| `config/tokenSummary.js` | Règles encart matériel (exclusions, fusion portes…). |
| `config/missionSites.js` | Liens communautaires (flyout). |

---

## Schéma `mission` (résumé)

Champs principaux : `questCode`, `title`, `authors[]`, `difficulty`, `playerCount`, `estimatedDuration`, `synopsis`, `objectives[]`, `specialRules[]`, `materialRequired`, `tilesUsed[]`, `pageTheme`, `pageEffect`, `footerLabel`, `mapImageDataUrl`, `cornerImage`, `cornerSide`.

Source complète : `defaultMission()` dans `utils/mission.js`. Persisté **dans** le JSON carte (`mapStore.mission`).

---

## Capture & impression

- **Capturer la carte** : `requestCanvasExportWithoutGrid` → stocke `mapImageDataUrl` (data URL, peut grossir le JSON).
- **Crop** : même logique que export en-tête (`mapExportBounds` via `CanvasGrid`) — voir [`CONTEXT_CANVAS.md`](CONTEXT_CANVAS.md).
- **Imprimer / PDF** : `window.print()` — CSS print sur `#mission-print-root` ; **100 % client**.

`CanvasGrid` reste monté (onglet Carte en `v-show`) : l’export doit fonctionner depuis l’onglet Mission.

---

## Mise en page adaptative (`MissionPagePreview`)

Logique **métier non triviale** — ne pas simplifier sans tests visuels :

| Computed | Rôle |
|----------|------|
| `tokenSummaryItems` | Jetons dérivés de `layers.objects` + `tokenSummary.js` + `assetDictionary`. |
| `tokenSummaryPlacement` | Encart matériel en colonne **intro** ou **rules** selon volume texte (`colChars`). |
| `tileChipsLayout` | Puces tuiles : `aside` (gauche carte), `rules` (sous règles), `none` — selon nb tuiles + chars totaux. |
| `topGridColumnsStyle` | Largeurs colonnes intro/rules proportionnelles au texte. |
| `tileGridLayout` | Grille visuelle tuiles (slots) si beaucoup de codes. |

**Décision produit** : une **seule page A4** ; affiner pour tenir sur une page (pas de pagination).

---

## Fidélité PDF officiel

Chaque **`pageTheme`** vise le style PDF de la série Zombicide correspondante :

- Polices / couleurs : variables CSS dans `mission-print.css` (`data-mission-theme='classic'` …).
- **Polices auto-hébergées** : fichiers `.woff2` dans `frontend/public/fonts/` — aucune requête CDN (compatible mode statique FTP). Détail : `docs/MISSION_FONTS.md`.
- Effets page : `mission.pageEffect` (`grain`, `sable`, `desert`, …).
- Décor coin : `cornerImage` + `cornerSide` filtrés par thème.

### Variables typographiques sémantiques

10 variables `--mp-font-*` par thème (sauf Fantasy qui conserve `--mp-title/body/flavor`) :

| Variable | Rôle | Classe(s) HTML |
|----------|------|----------------|
| `--mp-font-quest` | Code mission | `.mp-quest-code` |
| `--mp-font-hero` | Titre mission / footer | `.mp-title`, `.mp-footer-label` |
| `--mp-font-meta` | Méta difficulté/joueurs | `.mp-meta-line` |
| `--mp-font-synopsis` | Texte synopsis | `.mp-synopsis` |
| `--mp-font-section` | Titres sections / aside | `.mp-section-title`, `.mp-aside-title` |
| `--mp-font-body` | Corps règles | `.mp-list`, `.mp-authors` |
| `--mp-font-label` | Labels dalles | `.mp-dalles-label`, `.mp-dalles-value` |
| `--mp-font-map` | Puces tuiles | `.mp-tile-chips` |
| `--mp-font-token-name` | Nom jetons | `.mp-ts-label` |
| `--mp-font-token-deco` | Chevrons encart jetons | `.mp-ts-chevrons span` |

**Références visuelles** : à documenter au fil de l'affinage (captures PDF officiels par série — dossier ou liens à définir dans le repo si besoin).
---

## Sync thèmes

- Changer la « série » dans `MissionEditor` → `themeStore.setTheme` → patch `mission.pageTheme`.
- Charger une carte → `mapStore.loadMap` applique `pageTheme` au `themeStore`.
- Filtre assets panneau gauche : `themeStore.assetGameTypeFilter` (peut diverger de `pageTheme` si filtre « all »).

Voir aussi [`CONTEXT_PACKS.md`](CONTEXT_PACKS.md) pour `gameType` des packs.
