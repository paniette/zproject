# Polices mission par thème — zproject

Tableau de référence des polices utilisées dans le rendu PDF de la page mission.  
Toutes les polices sont auto-hébergées dans `frontend/public/fonts/` et chargées via `@font-face` dans `frontend/src/assets/mission-fonts.css`. Aucune requête CDN lors du rendu (compatible mode statique FTP).

Pour régénérer les fichiers `.woff2` : `bash scripts/fetch_mission_fonts.sh`  
Licences détaillées : [`frontend/public/fonts/LICENSES.md`](../frontend/public/fonts/LICENSES.md)

---

## Classic (Zombicide 1ère édition, 2012–2018)

Référence officielle : Interstate Condensed (titres), Gorri Sans (synopsis).  
Équivalences libres :

| Rôle PDF | Variable CSS | Police locale | Famille Google/Source | Licence | Fidélité |
|----------|-------------|---------------|-----------------------|---------|----------|
| Code mission | `--mp-font-quest` | `classic/creepster.woff2` | Creepster | OFL | Approximative (style grunge) |
| Titre mission | `--mp-font-hero` | `classic/creepster.woff2` | Creepster | OFL | Approximative |
| Méta joueurs/difficulté | `--mp-font-meta` | `shared/tex-gyre-heros/` | TeX Gyre Heros (≈ Helvetica Neue) | GUST libre | Bonne |
| Synopsis | `--mp-font-synopsis` | `shared/gorri-sans.woff2` | Gorri Sans | OFL | Très bonne (police originale) |
| Titres section | `--mp-font-section` | `shared/tex-gyre-heros/` | TeX Gyre Heros Bold | GUST libre | Bonne |
| Corps règles | `--mp-font-body` | `shared/tex-gyre-heros/` | TeX Gyre Heros | GUST libre | Bonne |
| Labels | `--mp-font-label` | `shared/tex-gyre-heros/` | TeX Gyre Heros | GUST libre | Bonne |
| Puces tuiles | `--mp-font-map` | `shared/tex-gyre-heros/` | TeX Gyre Heros | GUST libre | Bonne |
| Nom jetons | `--mp-font-token-name` | `classic/creepster.woff2` | Creepster | OFL | Approximative |
| Chevrons décor | `--mp-font-token-deco` | `shared/wc-rhesus-b.woff2` | WC Rhesus B Bta | 100% Free | Bonne |

---

## Modern (Zombicide 2ème édition, depuis 2020 — référence WM44)

Référence officielle : Interstate Bold Condensed (code/titres), Gorri Sans (synopsis), Source Sans Pro Light (corps).

| Rôle PDF | Variable CSS | Police locale | Fidélité |
|----------|-------------|---------------|----------|
| Code mission (24 pt condensed) | `--mp-font-quest` | `modern/league-gothic.woff2` | Bonne (condensed similaire) |
| Titre mission (16 pt condensed italic) | `--mp-font-hero` | `modern/league-gothic.woff2` | Bonne |
| Méta (9 pt black) | `--mp-font-meta` | `shared/overpass/overpass-black.woff2` | Bonne |
| Synopsis (8,5 pt) | `--mp-font-synopsis` | `shared/gorri-sans.woff2` | Très bonne (police originale) |
| Titres section (11 pt black) | `--mp-font-section` | `shared/overpass/overpass-extrabold.woff2` | Bonne |
| Corps règles (9 pt light) | `--mp-font-body` | `shared/source-sans-3/source-sans-3-light.woff2` | Très bonne (≈ Source Sans Pro) |
| Labels | `--mp-font-label` | `shared/source-sans-3/source-sans-3-semibold.woff2` | Très bonne |
| Puces tuiles | `--mp-font-map` | `shared/overpass/overpass-extrabold.woff2` | Bonne |
| Nom jetons | `--mp-font-token-name` | `modern/capture-it.woff2` | Approximative (style imprimé) |
| Chevrons décor | `--mp-font-token-deco` | `shared/wc-rhesus-b.woff2` | Bonne |

---

## Western (Undead or Alive)

Référence officielle : Fairplex (titres condensed), Trilby (corps serif), CornDog (décor).

| Rôle PDF | Variable CSS | Police locale | Fidélité |
|----------|-------------|---------------|----------|
| Code / titre | `--mp-font-quest` / `--mp-font-hero` | `western/rye.woff2` | Approximative (style western) |
| Méta | `--mp-font-meta` | `shared/overpass/overpass-black.woff2` | Correcte |
| Synopsis / corps | `--mp-font-synopsis` / `--mp-font-body` | `shared/roboto-slab/roboto-slab-regular.woff2` | Correcte (≈ serif western) |
| Titres section | `--mp-font-section` | `shared/roboto-slab/roboto-slab-bold.woff2` | Correcte |
| Labels | `--mp-font-label` | `shared/roboto-slab/roboto-slab-bold.woff2` | Correcte |
| Puces tuiles | `--mp-font-map` | `shared/overpass/overpass-extrabold.woff2` | Correcte |
| Nom jetons | `--mp-font-token-name` | `shared/roboto-slab/roboto-slab-regular.woff2` | Correcte |
| Chevrons décor | `--mp-font-token-deco` | `shared/wc-rhesus-b.woff2` | Bonne |

---

## Sci-Fi (Invader / Dark Side / Massive Darkness 2)

Référence officielle : Zekton (titres/codes), Helvetica Neue (corps).

| Rôle PDF | Variable CSS | Police locale | Fidélité |
|----------|-------------|---------------|----------|
| Code / titre | `--mp-font-quest` / `--mp-font-hero` | `scifi/zekton.woff2` | Très bonne (police originale Typodermic) |
| Méta | `--mp-font-meta` | `shared/tex-gyre-heros/` | Bonne (≈ Helvetica Neue) |
| Synopsis / corps | `--mp-font-synopsis` / `--mp-font-body` | `shared/tex-gyre-heros/` | Bonne |
| Titres section | `--mp-font-section` | `scifi/zekton.woff2` | Très bonne |
| Labels | `--mp-font-label` | `shared/tex-gyre-heros/` | Bonne |
| Puces tuiles | `--mp-font-map` | `scifi/michroma.woff2` | Correcte (style techno) |
| Nom jetons | `--mp-font-token-name` | `scifi/michroma.woff2` | Correcte |
| Chevrons décor | `--mp-font-token-deco` | `shared/wc-rhesus-b.woff2` | Bonne |

---

## Night / NOTLD (Night of the Living Dead)

Référence officielle : Vista Slab (corps serif), Mr Black / Tiger (titres impact), Metallophile Sp8 (décor).

| Rôle PDF | Variable CSS | Police locale | Fidélité |
|----------|-------------|---------------|----------|
| Code / titre (impact) | `--mp-font-quest` / `--mp-font-hero` | `night/anton.woff2` | Bonne (style impact/affiche) |
| Méta | `--mp-font-meta` | `night/jost-medium.woff2` | Correcte |
| Synopsis / corps | `--mp-font-synopsis` / `--mp-font-body` | `shared/roboto-slab/roboto-slab-regular.woff2` | Correcte (≈ serif slab) |
| Titres section | `--mp-font-section` | `night/jost-medium.woff2` | Correcte |
| Labels | `--mp-font-label` | `night/jost-medium.woff2` | Correcte |
| Puces tuiles (machine à écrire) | `--mp-font-map` | `night/special-elite.woff2` | Bonne (style retro typewriter) |
| Nom jetons | `--mp-font-token-name` | `night/special-elite.woff2` | Bonne |
| Chevrons décor | `--mp-font-token-deco` | `shared/wc-rhesus-b.woff2` | Bonne |

---

## Fantasy (Green Horde / Black Plague — règles CSS inchangées)

Fantasy conserve ses polices commerciales (Algo FY Black, Arek Latin) existantes.  
`UnifrakturMaguncia` (titres/dropcap), `IM Fell English` (corps fallback) et `Cinzel` (titre fallback) sont maintenant **locaux** (`shared/`), déclarés dans `mission-fonts.css`.  
**0 requête CDN** — toutes les polices sont auto-hébergées. Les règles CSS Fantasy dans `mission-print.css` sont **intouchables**.

---

## Architecture des fichiers

```
frontend/
├── public/fonts/           # Polices versionnées (woff2)
│   ├── LICENSES.md
│   ├── shared/             # Partagées multi-thèmes
│   └── modern|classic|western|scifi|night/
└── src/assets/
    ├── mission-fonts.css   # @font-face — chargé en premier dans MissionPagePreview.vue
    └── mission-print.css   # --mp-font-* par thème + couleurs + @media print
scripts/
└── fetch_mission_fonts.sh  # Script de re-téléchargement/conversion (sans npm)
```

## Mode statique

Polices dans `public/fonts/` → copiées dans `dist/fonts/` par `vite build` → déploiement FTP direct.  
Vérification : `npm run build && grep -r "cdnfonts\|googleapis.com/css2" dist/` ne doit retourner **aucun résultat** (0 CDN pour tous les thèmes y compris Fantasy).
