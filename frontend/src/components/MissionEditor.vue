<template>
  <div class="mission-editor">
    <div class="mission-form">
      <h2 class="mission-form-title">{{ $t('missionEditor.title') }}</h2>

      <div class="field">
        <span>{{ $t('missionEditor.series') }}</span>
        <div
          class="game-type-filter"
          :class="{ 'has-selection': themeStore.activeTheme !== '' }"
          role="group"
          :aria-label="$t('missionEditor.seriesAriaLabel')"
        >
          <button
            v-for="gt in gameTypes"
            :key="t.id"
            type="button"
            class="gt-btn"
            :class="{ active: themeStore.activeTheme === gt.id }"
            :title="gt.label"
            @click="themeStore.setTheme(gt.id)"
          >
            <img class="gt-icon" :src="getGameTypeIcon(gt.id)" :alt="gt.label" />
            <span class="sr-only">{{ gt.label }}</span>
          </button>
        </div>
      </div>

      <label class="field">
        <span>{{ $t('missionEditor.pageEffect') }}</span>
        <select v-model="mission.pageEffect" class="input">
          <option value="none">{{ $t('missionEditor.effects.none') }}</option>
          <option value="grain">{{ $t('missionEditor.effects.grain') }}</option>
          <option value="tache">{{ $t('missionEditor.effects.tache') }}</option>
          <option value="sable">{{ $t('missionEditor.effects.sable') }}</option>
          <option value="froisse">{{ $t('missionEditor.effects.froisse') }}</option>
          <option value="desert">{{ $t('missionEditor.effects.desert') }}</option>
        </select>
      </label>

      <div v-if="availableCornerImages.length" class="field">
        <span>{{ $t('missionEditor.cornerDeco') }}</span>
        <div class="field-row">
          <select
            :value="mission.cornerImage || ''"
            class="input flex-1"
            @change="patchCornerImage($event.target.value)"
          >
            <option value="">{{ $t('missionEditor.noCorner') }}</option>
            <option v-for="img in availableCornerImages" :key="img.id" :value="img.file">
              {{ img.label }}
            </option>
          </select>
          <select
            v-if="mission.cornerImage"
            :value="mission.cornerSide || 'left'"
            class="input"
            style="width: 110px"
            @change="patchCornerSide($event.target.value)"
          >
            <option value="left">{{ $t('missionEditor.cornerLeft') }}</option>
            <option value="right">{{ $t('missionEditor.cornerRight') }}</option>
          </select>
        </div>
      </div>

      <label class="field">
        <span>{{ $t('missionEditor.questCode') }}</span>
        <input v-model="mission.questCode" type="text" class="input" placeholder="B61" />
      </label>

      <label class="field">
        <span>{{ $t('missionEditor.missionTitle') }}</span>
        <input v-model="mission.title" type="text" class="input" :placeholder="$t('missionEditor.titlePlaceholder')" />
      </label>

      <label class="field">
        <span>{{ $t('missionEditor.authors') }}</span>
        <textarea v-model="authorsText" class="input textarea" rows="3" :placeholder="$t('missionEditor.authorsPlaceholder')"></textarea>
      </label>

      <div class="field-row">
        <label class="field half">
          <span>{{ $t('missionEditor.difficulty') }}</span>
          <input v-model="mission.difficulty" type="text" class="input" placeholder="HARD" />
        </label>
        <label class="field half">
          <span>{{ $t('missionEditor.players') }}</span>
          <input v-model="mission.playerCount" type="text" class="input" :placeholder="$t('missionEditor.playersPlaceholder')" />
        </label>
        <label class="field half">
          <span>{{ $t('missionEditor.duration') }}</span>
          <input v-model="mission.estimatedDuration" type="text" class="input" placeholder="MEDIUM" />
        </label>
      </div>

      <label class="field">
        <span>{{ $t('missionEditor.synopsis') }}</span>
        <textarea v-model="mission.synopsis" class="input textarea" rows="6" :placeholder="$t('missionEditor.synopsisPlaceholder')"></textarea>
      </label>

      <label class="field">
        <span>{{ $t('missionEditor.objectives') }}</span>
        <textarea v-model="objectivesText" class="input textarea" rows="8"></textarea>
      </label>

      <label class="field">
        <span>{{ $t('missionEditor.specialRules') }}</span>
        <textarea v-model="specialRulesText" class="input textarea" rows="8"></textarea>
      </label>

      <label class="field">
        <span>{{ $t('missionEditor.material') }}</span>
        <input
          v-model="mission.materialRequired"
          type="text"
          class="input"
          :placeholder="$t('missionEditor.materialPlaceholder')"
        />
      </label>

      <label class="field">
        <span>{{ $t('missionEditor.footerLabel') }}</span>
        <input
          v-model="mission.footerLabel"
          type="text"
          class="input"
          :placeholder="$t('missionEditor.footerLabelPlaceholder')"
        />
      </label>

      <div class="field">
        <span>{{ $t('missionEditor.tilesUsed') }}</span>
        <div class="tiles-row">
          <input v-model="tilesText" type="text" class="input flex-1" :placeholder="$t('missionEditor.tilesUsedPlaceholder')" />
          <button type="button" class="btn-secondary" @click="syncTiles">{{ $t('missionEditor.fromMap') }}</button>
        </div>
      </div>

      <div class="field actions">
        <button type="button" class="btn-primary" @click="captureMap">{{ $t('missionEditor.captureMap') }}</button>
        <button v-if="mission.mapImageDataUrl" type="button" class="btn-secondary" @click="clearMapImage">{{ $t('missionEditor.removeImage') }}</button>
        <button type="button" class="btn-secondary" @click="printPreview">{{ $t('missionEditor.print') }}</button>
      </div>
    </div>

    <div class="mission-preview-panel">
      <h2 class="mission-form-title">{{ $t('missionEditor.previewTitle') }}</h2>
      <div class="preview-scroll">
        <MissionPagePreview />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import { useMapStore } from '@/stores/mapStore'
import { useThemeStore } from '@/stores/themeStore'
import { deriveTilesFromLayers } from '@/utils/mission'
import { requestCanvasExportWithoutGrid } from '@/services/canvasExport'
import { GAME_TYPES } from '@/config/gameTypes'
import { CORNER_IMAGES } from '@/config/missionCornerImages'
import iconClassic from '@/assets/images/menu-setting-classic.jpg'
import iconModern from '@/assets/images/menu-setting-modern.jpg'
import iconFantasy from '@/assets/images/menu-setting-fantasy.jpg'
import iconWestern from '@/assets/images/menu-setting-western.jpg'
import iconScifi from '@/assets/images/menu-setting-scifi.jpg'
import iconNight from '@/assets/images/menu-setting-night.jpg'
import MissionPagePreview from './MissionPagePreview.vue'

const { t } = useI18n()
const mapStore = useMapStore()
const themeStore = useThemeStore()
const { mission } = storeToRefs(mapStore)

const gameTypes = GAME_TYPES.filter(t => t.id !== 'all')

const availableCornerImages = computed(() => CORNER_IMAGES[themeStore.activeTheme] ?? [])

function patchCornerImage (file) {
  mapStore.patchMission({ cornerImage: file || null })
}

function patchCornerSide (side) {
  mapStore.patchMission({ cornerSide: side })
}

const iconById = {
  classic: iconClassic,
  modern: iconModern,
  fantasy: iconFantasy,
  western: iconWestern,
  scifi: iconScifi,
  night: iconNight
}

function getGameTypeIcon (id) {
  return iconById[id] || ''
}

/** Conserve espaces et retours à la ligne en cours de frappe (pas de trim par ligne). */
function linesToArray (text) {
  if (text == null || text === '') return []
  return text.split(/\r?\n/)
}

function arrayToLines (arr) {
  return (arr && arr.length) ? arr.join('\n') : ''
}

const authorsText = computed({
  get: () => arrayToLines(mission.value.authors),
  set: (v) => {
    mapStore.patchMission({ authors: linesToArray(v) })
  }
})

const objectivesText = computed({
  get: () => arrayToLines(mission.value.objectives),
  set: (v) => {
    mapStore.patchMission({ objectives: linesToArray(v) })
  }
})

const specialRulesText = computed({
  get: () => arrayToLines(mission.value.specialRules),
  set: (v) => {
    mapStore.patchMission({ specialRules: linesToArray(v) })
  }
})

const tilesText = computed({
  get: () => (mission.value.tilesUsed || []).join(', '),
  set: (v) => {
    const parts = String(v ?? '')
      .split(/[,;]+/)
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean)
    mapStore.patchMission({ tilesUsed: parts })
  }
})

function syncTiles () {
  const codes = deriveTilesFromLayers(mapStore.layers)
  mapStore.patchMission({ tilesUsed: codes })
}

async function captureMap () {
  try {
    const dataUrl = await requestCanvasExportWithoutGrid({ mimeType: 'image/png', quality: 0.92 })
    mapStore.patchMission({ mapImageDataUrl: dataUrl })
  } catch (e) {
    console.error(e)
    const msg = e?.message || ''
    alert(
      msg || t('missionEditor.captureError')
    )
  }
}

function clearMapImage () {
  mapStore.patchMission({ mapImageDataUrl: null })
}

function printPreview () {
  window.print()
}

watch(
  () => mission.value.pageTheme,
  (id) => {
    const el = document.getElementById('mission-print-root')
    if (el) el.setAttribute('data-mission-theme', id || 'classic')
  }
)
</script>

<style scoped>
.game-type-filter {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
  width: 100%;
  padding: 4px 0;
  overflow: visible;
  align-items: center;
}

.gt-btn {
  width: auto;
  height: 44px;
  padding: 0;
  border-radius: 6px;
  border: 1px solid color-mix(in srgb, var(--primary-color) 55%, #000);
  background: rgba(0, 0, 0, 0.22);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  flex: 1 1 0;
  min-width: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: transform 140ms ease, background-color 140ms ease, border-color 140ms ease;
  transform-origin: center;
}

.gt-btn.active {
  background: color-mix(in srgb, var(--primary-color) 35%, #000);
  border-color: var(--primary-color);
}

.game-type-filter.has-selection .gt-btn {
  transform: scale(0.92);
}

.game-type-filter.has-selection .gt-btn.active {
  transform: scale(1.12);
}

.game-type-filter.has-selection .gt-btn:not(.active):hover {
  transform: scale(0.96);
}

.game-type-filter:not(.has-selection):has(.gt-btn:hover) .gt-btn {
  transform: scale(0.92);
}

.game-type-filter:not(.has-selection):has(.gt-btn:hover) .gt-btn:hover {
  transform: scale(1.12);
}

.game-type-filter:not(.has-selection) .gt-btn:hover {
  transform: scale(1.12);
}

.gt-btn:active {
  transform: scale(1.10);
}

.gt-icon {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  object-position: center;
  image-rendering: auto;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.mission-editor {
  display: flex;
  width: 100%;
  height: 100%;
  min-height: 0;
  background: var(--gray-dark);
  color: var(--light-color);
}

.mission-form {
  width: 42%;
  min-width: 280px;
  max-width: 520px;
  padding: 16px 20px;
  overflow-y: auto;
  border-right: 2px solid var(--brown-medium);
  box-sizing: border-box;
}

.mission-preview-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
}

.mission-form-title {
  font-family: 'Creepster', cursive;
  font-size: 1.4rem;
  font-weight: normal;
  color: var(--primary-color);
  margin: 0 0 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}

.field > span {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

.field-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.field.half {
  flex: 1 1 120px;
  min-width: 100px;
}

.input {
  padding: 8px 10px;
  border-radius: 4px;
  border: 1px solid var(--brown-light);
  background: rgba(255, 255, 255, 0.08);
  color: white;
  font-size: 14px;
}

.input::placeholder {
  color: rgba(255, 255, 255, 0.45);
}

.textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.tiles-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.flex-1 {
  flex: 1;
  min-width: 0;
}

.btn-primary,
.btn-secondary {
  padding: 8px 14px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  border: 2px solid var(--brown-light);
}

.btn-primary {
  background: var(--brown-medium);
  color: white;
}

.btn-secondary {
  background: transparent;
  color: white;
}

.actions {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 8px;
}

.preview-scroll {
  flex: 1;
  min-height: 0;
  overflow: auto;
  -webkit-overflow-scrolling: touch;
  padding: 8px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 6px;
}

@media print {
  .mission-form,
  .mission-form-title,
  .mission-preview-panel > h2 {
    display: none !important;
  }
  .mission-editor {
    display: block;
    min-height: 297mm;
    background: transparent;
    color: black;
  }
  .mission-preview-panel {
    padding: 0;
    min-height: 297mm;
  }
  .preview-scroll {
    overflow: visible;
    background: none;
    padding: 0;
    min-height: 297mm;
  }
}
</style>