<template>
  <div
    class="mission-page-preview"
    :data-mission-theme="pageThemeId"
    id="mission-print-root"
  >
    <div class="mp-sheet">
      <div class="mp-sheet-inner">
        <header class="mp-hero">
          <p v-if="mission.questCode" class="mp-quest-code">QUÊTE {{ mission.questCode }}</p>
          <h1 class="mp-title">{{ displayTitle }}</h1>
          <p class="mp-meta-line">
            <template v-if="infoLine">{{ infoLine }}</template>
            <template v-else>&nbsp;</template>
          </p>
        </header>

        <div class="mp-top-grid" :style="topGridColumnsStyle">
          <div class="mp-col-intro">
            <p v-if="authorsLine" class="mp-authors">{{ authorsLine }}</p>
            <section v-if="mission.synopsis" class="mp-synopsis-block">
              <p class="mp-synopsis mp-synopsis--dropcap">{{ mission.synopsis }}</p>
            </section>
          </div>

          <div class="mp-col-rules">
            <section v-if="tilesLine" class="mp-dalles">
              <div class="mp-dalles-left">
                <h2 class="mp-section-title">Dalles requises</h2>
                <p class="mp-dalles-line">{{ tilesLine }}</p>
                <!-- Chips de repli : seulement si pas de tuiles posées sur la carte -->
                <ul
                  v-if="tileChipsLayout === 'rules' && !tileGridLayout"
                  class="mp-tile-chips mp-tile-chips--in-column"
                  aria-label="Tuiles"
                >
                  <li v-for="code in tilesUsed" :key="'chip-col-' + code">{{ code }}</li>
                </ul>
              </div>
              <div v-if="tileGridLayout" class="mp-tile-layout-preview" aria-label="Placement des tuiles">
                <div v-for="r in tileGridLayout.rows" :key="r" class="mp-tlp-row">
                  <span
                    v-for="c in tileGridLayout.cols"
                    :key="c"
                    class="mp-tlp-cell"
                    :class="{ 'mp-tlp-cell--on': tileGridLayout.slotCodes.has(`${c-1},${r-1}`) }"
                  >{{ tileGridLayout.slotCodes.get(`${c-1},${r-1}`) ?? '' }}</span>
                </div>
              </div>
            </section>

            <section v-if="mission.objectives.length" class="mp-block">
              <h2 class="mp-section-title">Objectifs</h2>
              <ul class="mp-list">
                <li v-for="(item, i) in mission.objectives" :key="'obj-' + i">{{ item }}</li>
              </ul>
            </section>

            <section v-if="mission.specialRules.length" class="mp-block">
              <h2 class="mp-section-title">Règles spéciales</h2>
              <ul class="mp-list">
                <li v-for="(item, i) in mission.specialRules" :key="'sr-' + i">{{ item }}</li>
              </ul>
            </section>
          </div>
        </div>

        <div
          class="mp-bottom-grid"
          :class="{
            'mp-bottom-grid--map-only': !tilesUsed.length || tileChipsLayout !== 'aside',
            'mp-bottom-grid--aside': tilesUsed.length && tileChipsLayout === 'aside'
          }"
        >
          <aside
            v-if="tilesUsed.length && tileChipsLayout === 'aside'"
            class="mp-tiles-aside"
            aria-label="Tuiles"
          >
            <h3 class="mp-aside-title">Tuiles</h3>
            <ul class="mp-tile-chips mp-tile-chips--aside">
              <li v-for="code in tilesUsed" :key="'chip-' + code">{{ code }}</li>
            </ul>
          </aside>

          <div class="mp-map-col">
            <section v-if="mission.mapImageDataUrl" class="mp-map-wrap">
              <img :src="mission.mapImageDataUrl" alt="Carte de la mission" class="mp-map-img" />
            </section>
            <p v-else class="mp-map-placeholder">Aucune carte capturée — utilisez « Capturer la carte » dans le panneau de gauche.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { storeToRefs } from 'pinia'

const mapStore = useMapStore()
const { mission } = storeToRefs(mapStore)

function mathGcd(a, b) {
  while (b) { [a, b] = [b, a % b] }
  return a
}

/**
 * Calcule le pas régulier entre tuiles (en cellules de grille) depuis les coordonnées du store.
 * Retourne un objet { slots, cols, rows } pour le rendu de la mini-grille de placement,
 * ou null si aucune tuile n'est posée.
 */
const tileGridLayout = computed(() => {
  const tiles = mapStore.layers.tiles
  if (!tiles || tiles.length === 0) return null

  const xs = [...new Set(tiles.map(t => t.x))].sort((a, b) => a - b)
  const ys = [...new Set(tiles.map(t => t.y))].sort((a, b) => a - b)

  let stepX = 0
  for (let i = 1; i < xs.length; i++) stepX = mathGcd(stepX, xs[i] - xs[i - 1])
  let stepY = 0
  for (let i = 1; i < ys.length; i++) stepY = mathGcd(stepY, ys[i] - ys[i - 1])

  const step = mathGcd(stepX || stepY || 25, stepY || stepX || 25) || 25
  const minX = xs[0]
  const minY = ys[0]

  // Map slot-key → code lisible (ex. "37R", "1V")
  const slotCodes = new Map()
  for (const t of tiles) {
    const col = Math.round((t.x - minX) / step)
    const row = Math.round((t.y - minY) / step)
    const m = t.asset.match(/(\d+[RV])\.(?:png|webp)/i)
    slotCodes.set(`${col},${row}`, m ? m[1].toUpperCase() : '?')
  }

  const cols = Math.round((xs[xs.length - 1] - minX) / step) + 1
  const rows = Math.round((ys[ys.length - 1] - minY) / step) + 1

  return { slotCodes, cols, rows }
})

const pageThemeId = computed(() => (mission.value.pageTheme ? mission.value.pageTheme : 'eternal'))
const displayTitle = computed(() => (mission.value.title ? mission.value.title : 'Sans titre'))

const tilesUsed = computed(() => {
  const t = mission.value.tilesUsed
  return Array.isArray(t) ? t : []
})

const infoLine = computed(() => {
  const m = mission.value
  const parts = [m.difficulty, m.playerCount, m.estimatedDuration].filter(Boolean)
  return parts.join(' / ')
})

const authorsLine = computed(() => {
  const a = mission.value.authors
  if (!a || !a.length) return ''
  return 'Par ' + a.join(', ')
})

const tilesLine = computed(() => {
  if (!tilesUsed.value.length) return ''
  return tilesUsed.value.join(', ')
})

/** Volume texte zone haute (synopsis, auteurs, dalles, listes) — heuristique mise en page tuiles. */
const topRegionCharCount = computed(() => {
  const m = mission.value
  let n = (m.synopsis || '').length
  n += authorsLine.value.length
  n += tilesLine.value.length
  n += (m.objectives || []).join('\n').length
  n += (m.specialRules || []).join('\n').length
  return n
})

/**
 * aside : puces à gauche de la carte (mission légère).
 * rules : carte pleine largeur en bas, puces sous « Dalles requises ».
 * none : pas de puces (liste texte dalles seulement si tuiles).
 */
const tileChipsLayout = computed(() => {
  const nTiles = tilesUsed.value.length
  if (!nTiles) return 'none'
  const chars = topRegionCharCount.value
  if (nTiles > 12 || chars > 3000) return 'none'
  if (nTiles > 6 || chars > 1100) return 'rules'
  return 'aside'
})

/** Largeurs de colonnes grosso modo proportionnelles au volume de texte (unités `fr`). */
const topGridColumnsStyle = computed(() => {
  const m = mission.value
  const introChars =
    (m.synopsis || '').length + (authorsLine.value ? authorsLine.value.length : 0)
  let rulesChars = tilesLine.value.length
  rulesChars += (m.objectives || []).join('\n').length
  rulesChars += (m.specialRules || []).join('\n').length
  if (tilesLine.value) rulesChars += 24
  if ((m.objectives || []).length) rulesChars += 20
  if ((m.specialRules || []).length) rulesChars += 28
  const a = Math.max(12, introChars)
  const b = Math.max(12, rulesChars)
  return { gridTemplateColumns: `${a}fr ${b}fr` }
})
</script>

<style scoped>
@import url('../assets/mission-print.css');

.mission-page-preview {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100%;
  padding: 0.5rem;
  box-sizing: border-box;
  font-family: var(--mp-body);
  color: var(--mp-ink);
}

.mp-sheet {
  width: min(100%, 210mm);
  aspect-ratio: 210 / 297;
  background: var(--mp-bg);
  box-shadow: 0 2px 14px rgba(0, 0, 0, 0.14);
  border-radius: 4px;
  box-sizing: border-box;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.mp-sheet-inner {
  flex: 1;
  min-height: 0;
  padding: clamp(10px, 3vw, 14mm);
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  /* overflow: hidden sur tous les écrans : le scroll est géré par .preview-scroll (externe).
     Cela évite que .mp-sheet-inner intercepte les events touch sur mobile (quel que soit la
     largeur de l'écran, y compris les grands téléphones en paysage > 768px). */
  overflow: hidden;
}

.mp-top-grid {
  display: grid;
  /* gridTemplateColumns défini en inline selon le volume synopsis / colonne droite */
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem 1rem;
  align-items: start;
}

.mp-col-intro {
  min-width: 0;
}

.mp-col-rules {
  min-width: 0;
}

.mp-authors {
  font-size: 0.82rem;
  font-style: italic;
  margin: 0 0 0.5rem;
  opacity: 0.92;
}

.mp-synopsis-block {
  margin: 0;
}

.mp-synopsis {
  margin: 0;
  font-family: var(--mp-flavor);
  line-height: 1.5;
  white-space: pre-wrap;
  font-size: 0.95rem;
}

.mp-synopsis--dropcap::first-letter {
  float: left;
  font-family: var(--mp-flavor);
  font-size: 2.65rem;
  line-height: 0.85;
  padding-right: 0.12em;
  margin-top: 0.06em;
  color: var(--mp-accent);
}

.mp-dalles {
  margin-bottom: 0.65rem;
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

.mp-dalles-left {
  flex: 1;
  min-width: 0;
}

/* Mini-grille de placement des tuiles */
.mp-tile-layout-preview {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding-top: 0.15rem;
}

.mp-tlp-row {
  display: flex;
  gap: 3px;
}

.mp-tlp-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 2px;
  border: 1px solid color-mix(in srgb, var(--mp-ink) 20%, transparent);
  box-sizing: border-box;
  font-size: 0.58rem;
  font-weight: 700;
  line-height: 1;
  color: transparent; /* cellule vide : pas de texte visible */
}

.mp-tlp-cell--on {
  background: color-mix(in srgb, var(--mp-accent) 12%, transparent);
  border-color: color-mix(in srgb, var(--mp-accent) 80%, var(--mp-ink) 20%);
  color: var(--mp-ink);
}

.mp-dalles-line {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.45;
  font-weight: 600;
}

.mp-block {
  margin-bottom: 0.55rem;
}

.mp-block:last-child {
  margin-bottom: 0;
}

.mp-section-title {
  font-family: var(--mp-title);
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0 0 0.28rem;
  color: var(--mp-accent);
  letter-spacing: 0.02em;
}

.mp-list {
  margin: 0;
  padding-left: 1.1rem;
  line-height: 1.42;
  font-size: 0.86rem;
}

.mp-list li {
  margin-bottom: 0.25rem;
}

.mp-hero {
  flex-shrink: 0;
  margin: 0 0 0.35rem;
  padding: 0 0 0.55rem;
  text-align: left;
  border-bottom: 1px solid color-mix(in srgb, var(--mp-ink) 18%, transparent);
}

.mp-quest-code {
  font-family: var(--mp-title);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--mp-quest);
  margin: 0 0 0.15rem;
}

.mp-title {
  font-family: var(--mp-title);
  font-size: clamp(1.25rem, 2.8vw, 1.85rem);
  font-weight: 700;
  margin: 0 0 0.25rem;
  line-height: 1.12;
  color: var(--mp-ink);
  letter-spacing: 0.02em;
}

.mission-page-preview[data-mission-theme='eternal'] .mp-title {
  text-transform: uppercase;
}

.mission-page-preview[data-mission-theme='classic'] .mp-title,
.mission-page-preview[data-mission-theme='necro'] .mp-title {
  color: var(--mp-accent);
  font-weight: normal;
}

.mission-page-preview[data-mission-theme='medieval'] .mp-title {
  font-family: "UnifrakturMaguntia", fantasy;
  font-weight: 400;
  color: var(--mp-accent);
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.mp-meta-line {
  font-family: var(--mp-title);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin: 0;
  opacity: 0.92;
}

.mp-bottom-grid {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
  align-items: stretch;
  margin-top: 0.15rem;
}

.mp-bottom-grid--aside {
  grid-template-columns: minmax(min-content, min(12%, 22mm)) 1fr;
}

.mp-bottom-grid--map-only {
  grid-template-columns: 1fr;
}

.mp-tiles-aside {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.mp-aside-title {
  font-family: var(--mp-title);
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin: 0;
  color: var(--mp-accent);
}

.mp-tile-chips {
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 0.68rem;
  font-weight: 700;
}

.mp-tile-chips--aside {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
}

.mp-tile-chips--in-column {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 6px;
  margin-top: 0.4rem;
  font-size: 0.72rem;
}

.mp-tile-chips li {
  border: 1px solid color-mix(in srgb, var(--mp-ink) 28%, transparent);
  padding: 3px 4px;
  text-align: center;
  line-height: 1.2;
}

.mp-tile-chips--in-column li {
  flex: 0 0 auto;
  min-width: 2.1em;
  padding: 2px 5px;
}

.mp-map-col {
  min-width: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.mp-map-wrap {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  /* Fond page : la capture PNG est transparente hors tuiles/jetons */
  background: var(--mp-bg);
}

.mp-map-img {
  width: 100%;
  height: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
}

.mp-map-placeholder {
  flex: 1;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 0.75rem;
  line-height: 1.4;
  opacity: 0.65;
  padding: 0.5rem;
}

@media print {
  .mission-page-preview {
    padding: 0;
    display: block;
    width: 100%;
    min-height: 297mm;
    box-sizing: border-box;
    background: var(--mp-bg);
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .mp-sheet {
    width: 100%;
    max-width: none;
    aspect-ratio: auto;
    min-height: 297mm;
    display: flex;
    flex-direction: column;
    box-shadow: none;
    border-radius: 0;
    overflow: visible;
    background: var(--mp-bg);
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .mp-sheet-inner {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: visible;
    padding: 10mm 12mm;
    gap: 0.5rem;
    box-sizing: border-box;
  }

  .mp-map-placeholder {
    min-height: 40mm;
  }
}
</style>
