# Annexe — Canvas & interactions carte

Normes pour `CanvasGrid.vue`, `mapStore`, `canvasRenderer.js`, `Toolbar.vue`, `toolStore.js`. Retour : [`CONTEXT.md`](CONTEXT.md).

---

## Offset global de grille

- État : **`gridOffsetX`**, **`gridOffsetY`** dans `mapStore`, action **`setGridOffset(x, y)`**.
- Le **pan** déplace cet offset : grille + contenu bougent ensemble.
- Coordonnées monde : case grille × `tileSize` + offset.

---

## Outils unifiés

L’outil **« place »** est fusionné avec **« move »** (`toolStore`) :

- Clic sur élément → sélection + drag.
- Clic case vide + asset sélectionné → placement + sélection.
- Sinon → **pan** (offset grille).

---

## Sélection

- Clic : sélection tuile/objet (sauf **delete**).
- Drop depuis panneau → **sélection auto** du nouvel élément.
- **Hover-to-selection** : `hoveredItem` pris en compte au clic.

---

## Coordonnées & zoom

- `getGridCoordinates` / `getGridCoordinatesWithSnap` (`canvasRenderer.js`) : intégrer **`gridOffsetX/Y`**, zoom, décalages vue.
- Zoom canvas : grille et éléments **alignés** (tests manuels zoom + pan + placement).

---

## Feedback visuel

- Survol : halo bleu, curseur selon outil (`move`, `delete`, `rotate`).
- Sélection : halo rouge (fond + contour).

---

## Export PNG (en-tête & capture mission)

- Pipeline commun : `CanvasGrid` + **`mapExportBounds.js`** (crop aux tuiles/objets posés).
- Demande async : `services/canvasExport.js` (`CANVAS_EXPORT_REQUEST` / `RESPONSE`).
- **Ne pas** appeler `canvas.toDataURL()` sur le canvas visible (grille + fond blanc).

---

## Checklist non-régression

1. Drop panneau → élément **sélectionné**.
2. Clic élément → **sélection** (selon outil).
3. Pan → grille + contenu **ensemble**.
4. Zoom → **alignement** conservé.
5. Outil move : drag, placer avec asset, pan sur vide.
6. Halos / curseurs **cohérents**.
7. Capture depuis onglet **Mission** → PNG sans grille.
8. Undo/redo inclut **mission** (`mapStore` historique).
