<template>
  <div class="mission-editor">
    <div class="mission-form">
      <h2 class="mission-form-title">Données de la mission</h2>

      <label class="field">
        <span>Thème de la page (typo)</span>
        <select v-model="mission.pageTheme" class="input">
          <option value="eternal">Empire (A4 blanc)</option>
          <option value="medieval">Médiéval (parchemin)</option>
          <option value="classic">Classique</option>
          <option value="slate">Ardoise</option>
          <option value="necro">Nécrose</option>
          <option value="abyss">Abyssal</option>
        </select>
      </label>

      <label class="field">
        <span>Code quête (ex. B61)</span>
        <input v-model="mission.questCode" type="text" class="input" placeholder="B61" />
      </label>

      <label class="field">
        <span>Titre</span>
        <input v-model="mission.title" type="text" class="input" placeholder="Titre de la mission" />
      </label>

      <label class="field">
        <span>Auteurs (un par ligne)</span>
        <textarea v-model="authorsText" class="input textarea" rows="3" placeholder="Nom Prénom"></textarea>
      </label>

      <div class="field-row">
        <label class="field half">
          <span>Difficulté</span>
          <input v-model="mission.difficulty" type="text" class="input" placeholder="HARD" />
        </label>
        <label class="field half">
          <span>Joueurs</span>
          <input v-model="mission.playerCount" type="text" class="input" placeholder="6 survivants" />
        </label>
        <label class="field half">
          <span>Durée estimée</span>
          <input v-model="mission.estimatedDuration" type="text" class="input" placeholder="MEDIUM" />
        </label>
      </div>

      <label class="field">
        <span>Synopsis</span>
        <textarea v-model="mission.synopsis" class="input textarea" rows="6" placeholder="Histoire..."></textarea>
      </label>

      <label class="field">
        <span>Objectifs (une ligne = un objectif)</span>
        <textarea v-model="objectivesText" class="input textarea" rows="8"></textarea>
      </label>

      <label class="field">
        <span>Règles spéciales (une ligne = une règle)</span>
        <textarea v-model="specialRulesText" class="input textarea" rows="8"></textarea>
      </label>

      <div class="field">
        <span>Tuiles utilisées</span>
        <div class="tiles-row">
          <input v-model="tilesText" type="text" class="input flex-1" placeholder="30V, 33R, 35V" />
          <button type="button" class="btn-secondary" @click="syncTiles">Depuis la carte</button>
        </div>
      </div>

      <div class="field actions">
        <button type="button" class="btn-primary" @click="captureMap">Capturer la carte (PNG)</button>
        <button v-if="mission.mapImageDataUrl" type="button" class="btn-secondary" @click="clearMapImage">Retirer l'image</button>
        <button type="button" class="btn-secondary" @click="printPreview">Imprimer / PDF</button>
      </div>
    </div>

    <div class="mission-preview-panel">
      <h2 class="mission-form-title">Prévisualisation</h2>
      <div class="preview-scroll">
        <MissionPagePreview />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useMapStore } from '@/stores/mapStore'
import { deriveTilesFromLayers } from '@/utils/mission'
import { requestCanvasExportWithoutGrid } from '@/services/canvasExport'
import MissionPagePreview from './MissionPagePreview.vue'

const mapStore = useMapStore()
const { mission } = storeToRefs(mapStore)

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
      msg ||
        'Impossible de capturer la carte (vérifiez que l’onglet Carte a bien chargé le canvas).'
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
    if (el) el.setAttribute('data-mission-theme', id || 'eternal')
  }
)
</script>

<style scoped>
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