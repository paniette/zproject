<template>
  <header class="app-header">
    <div class="header-content">
      <div class="header-left">
        <div class="logo">Zombicide Editor</div>
        <span class="save-status" :class="{ dirty: mapStore.isUnsaved }" :title="saveStatusTitle">
          {{ mapStore.isUnsaved ? 'Modifié' : 'Enregistré' }}
        </span>
      </div>
      <nav class="header-nav">
        <div class="nav-group">
          <div class="editor-tabs">
            <router-link to="/" class="nav-tab" active-class="nav-tab-active">Carte</router-link>
            <router-link to="/mission" class="nav-tab" active-class="nav-tab-active">Mission</router-link>
          </div>
        </div>

        <div v-if="menuVis.themeSelector || menuVis.userSelector" class="nav-group">
          <ThemeSelector v-if="menuVis.themeSelector" />
          <UserSelector v-if="menuVis.userSelector" />
        </div>

        <div class="nav-group">
          <button
            type="button"
            class="header-btn header-btn-icon"
            :disabled="!mapStore.canUndo"
            title="Annuler (Ctrl+Z)"
            @click="mapStore.undo()"
          >
            <MenuGlyph name="undo" />
            <span class="sr-only">Annuler</span>
          </button>
          <button
            type="button"
            class="header-btn header-btn-icon"
            :disabled="!mapStore.canRedo"
            title="Rétablir (Ctrl+Y)"
            @click="mapStore.redo()"
          >
            <MenuGlyph name="redo" />
            <span class="sr-only">Rétablir</span>
          </button>
          <button
            type="button"
            class="header-btn"
            :class="{ active: mapStore.isPreviewMode }"
            :title="mapStore.isPreviewMode ? 'Quitter l’aperçu' : 'Aperçu lecture seule'"
            @click="togglePreview"
          >
            {{ mapStore.isPreviewMode ? 'Quitter aperçu' : 'Aperçu' }}
          </button>
          <button type="button" class="header-btn header-btn-icon" title="Charger une carte" @click="openMapLoader">
            <MenuGlyph name="load" />
            <span class="sr-only">Charger</span>
          </button>
          <button type="button" class="header-btn header-btn-icon" title="Sauvegarder (Ctrl+S)" @click="saveMap">
            <MenuGlyph name="save" />
            <span class="sr-only">Sauvegarder</span>
          </button>
        </div>

        <div v-if="showExportsGroup" class="nav-group">
          <button
            v-if="menuVis.exportJson"
            type="button"
            class="header-btn"
            title="Télécharger le scénario JSON"
            @click="exportScenarioJson"
          >
            JSON
          </button>
          <button
            v-if="menuVis.exportXml"
            type="button"
            class="header-btn"
            title="Exporter en XML simplifié"
            @click="exportScenarioXml"
          >
            XML
          </button>
          <button
            v-if="menuVis.versions"
            type="button"
            class="header-btn"
            @click="showVersionsModal = true"
          >
            Versions
          </button>
        </div>

        <div class="nav-group">
          <button type="button" class="header-btn" title="Exporter en image PNG/JPEG" @click="exportMap">Image</button>
        </div>

        <div v-if="menuVis.uploadZip || menuVis.uploadElement" class="nav-group">
          <button v-if="menuVis.uploadZip" type="button" class="header-btn" @click="openPackZipUploader">Upload Pack ZIP</button>
          <button v-if="menuVis.uploadElement" type="button" class="header-btn" @click="openPackUploader">Upload Pack Element</button>
        </div>
      </nav>
    </div>
    <MapLoader :show="showMapLoader" @close="closeMapLoader" @load="handleMapLoad" />
    <PackZipUploader v-if="showPackZipUploader" @close="closePackZipUploader" />
    <PackUploader v-if="showPackUploader" @close="closePackUploader" />
    <MapVersionsModal :show="showVersionsModal" @close="showVersionsModal = false" />
    <SaveMapModal
      :show="showSaveModal"
      :initial-name="mapStore.mapName"
      @close="showSaveModal = false"
      @submit="handleSaveNameSubmit"
    />
  </header>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import ThemeSelector from './ThemeSelector.vue'
import UserSelector from './UserSelector.vue'
import MapLoader from './MapLoader.vue'
import PackZipUploader from './PackZipUploader.vue'
import PackUploader from './PackUploader.vue'
import MapVersionsModal from './MapVersionsModal.vue'
import MenuGlyph from './MenuGlyph.vue'
import SaveMapModal from './SaveMapModal.vue'
import { useMapStore } from '@/stores/mapStore'
import { useUserStore } from '@/stores/userStore'
import { config } from '@/config'
import api from '@/services/api'
import { requestCanvasExportWithoutGrid } from '@/services/canvasExport'
import { pushVersion } from '@/services/mapVersions'
import { mapPayloadToXml } from '@/utils/mapExportXml'
import { getEditorMenuVisibility } from '@/config/editorMenu'

const mapStore = useMapStore()
const userStore = useUserStore()

const showMapLoader = ref(false)
const showPackZipUploader = ref(false)
const showPackUploader = ref(false)
const showVersionsModal = ref(false)
const showSaveModal = ref(false)
const pendingSave = ref(false)

const isUnsaved = ref(true)

const saveStatusTitle = computed(() =>
  mapStore.isUnsaved
    ? 'Modifications non sauvegardées sur le serveur (ou brouillon local)'
    : 'Dernière sauvegarde reconnue pour cette session'
)

const menuVis = computed(() => getEditorMenuVisibility())

const showExportsGroup = computed(
  () => menuVis.value.exportJson || menuVis.value.exportXml || menuVis.value.versions
)

function buildMapPayload () {
  return {
    id: mapStore.currentMapId || undefined,
    name: mapStore.mapName,
    pack: mapStore.currentPack,
    grid: {
      width: mapStore.gridSize.width,
      height: mapStore.gridSize.height,
      tileSize: mapStore.tileSize
    },
    layers: JSON.parse(JSON.stringify(mapStore.layers)),
    gridOffsetX: mapStore.gridOffsetX,
    gridOffsetY: mapStore.gridOffsetY,
    mission: JSON.parse(JSON.stringify(mapStore.mission))
  }
}

function downloadTextFile (filename, text, mime) {
  const blob = new Blob([text], { type: mime || 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

function exportScenarioJson () {
  const payload = buildMapPayload()
  const name = (mapStore.mapName || 'scenario').replace(/[^\w\-]+/g, '_')
  downloadTextFile(`${name}_${new Date().toISOString().slice(0, 10)}.json`, JSON.stringify(payload, null, 2), 'application/json')
}

function exportScenarioXml () {
  const payload = buildMapPayload()
  const name = (mapStore.mapName || 'scenario').replace(/[^\w\-]+/g, '_')
  downloadTextFile(`${name}_${new Date().toISOString().slice(0, 10)}.xml`, mapPayloadToXml(payload), 'application/xml;charset=utf-8')
}

function togglePreview () {
  mapStore.setPreviewMode(!mapStore.isPreviewMode)
}

watch(() => mapStore.currentMapId, (newId) => {
  if (newId) {
    isUnsaved.value = false
  } else {
    isUnsaved.value = true
  }
})

const openPackUploader = () => {
  showPackUploader.value = true
}

const closePackUploader = () => {
  showPackUploader.value = false
}

const openMapLoader = () => {
  showMapLoader.value = true
}

const closeMapLoader = () => {
  showMapLoader.value = false
}

const openPackZipUploader = () => {
  showPackZipUploader.value = true
}

const closePackZipUploader = () => {
  showPackZipUploader.value = false
}

const handleMapLoad = (mapData) => {
  mapStore.loadMap(mapData)
  isUnsaved.value = false
  closeMapLoader()
}

// Keyboard shortcut for save
onMounted(() => {
  if (mapStore.mapName && mapStore.currentMapId) {
    isUnsaved.value = false
  } else {
    isUnsaved.value = true
  }
  
  const handleKeyDown = (e) => {
    const tag = (e.target && e.target.tagName) || ''
    const inField = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT'
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault()
      saveMap()
      return
    }
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && (e.key === 'z' || e.key === 'Z')) {
      if (inField) return
      e.preventDefault()
      mapStore.undo()
      return
    }
    if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || e.key === 'Y')) {
      if (inField) return
      e.preventDefault()
      mapStore.redo()
      return
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'z' || e.key === 'Z')) {
      if (inField) return
      e.preventDefault()
      mapStore.redo()
    }
  }
  window.addEventListener('keydown', handleKeyDown)
  
  return () => {
    window.removeEventListener('keydown', handleKeyDown)
  }
})

function ensureMapNameForSave () {
  const hasName = !!(mapStore.mapName && String(mapStore.mapName).trim())
  if (hasName) return true
  showSaveModal.value = true
  pendingSave.value = true
  return false
}

async function handleSaveNameSubmit (name) {
  mapStore.mapName = String(name).trim()
  showSaveModal.value = false
  if (pendingSave.value) {
    pendingSave.value = false
    await saveMap()
  }
}

const saveMap = async () => {
  try {
    if (!ensureMapNameForSave()) return
    
    const mapData = {
      ...buildMapPayload(),
      metadata: {
        created: mapStore.currentMapId ? undefined : new Date().toISOString(),
        modified: new Date().toISOString(),
        author: userStore.currentUser
      }
    }
    delete mapData.id

    if (mapStore.currentMapId) {
      const response = await api.updateMap(userStore.currentUser, mapStore.currentMapId, mapData)
      mapStore.currentMapId = response.data.id
    } else {
      const response = await api.createMap(userStore.currentUser, mapData)
      mapStore.currentMapId = response.data.id
    }
    isUnsaved.value = false
    mapStore.isUnsaved = false
    try {
      const snapshot = { ...buildMapPayload(), id: mapStore.currentMapId }
      pushVersion(mapStore.currentMapId || 'draft', 'Sauvegarde', snapshot)
    } catch (verErr) {
      console.warn('Version locale non enregistrée', verErr)
    }
    alert('Carte sauvegardée avec succès!' + (config.staticMode ? ' (sauvegardée localement)' : ''))
  } catch (error) {
    console.error('Error saving map:', error)
    alert('Erreur lors de la sauvegarde: ' + (error.response?.data?.error || error.message))
  }
}

const exportMap = () => {
  // Show export modal
  const format = prompt('Format (png/jpeg):', 'png')
  if (!format) return
  
  const showGrid = confirm('Afficher la grille?')
  const resolution = prompt('Résolution (1=standard, 2=2x, 4=4x):', '1')
  const scale = parseFloat(resolution) || 1
  
  // Get canvas from CanvasGrid
  const canvas = document.querySelector('canvas')
  if (!canvas) {
    alert('Canvas non trouvé')
    return
  }
  
  // Create export canvas
  const exportCanvas = document.createElement('canvas')
  const ctx = exportCanvas.getContext('2d')
  const tileSize = mapStore.tileSize * scale
  const width = mapStore.gridSize.width * tileSize
  const height = mapStore.gridSize.height * tileSize
  
  exportCanvas.width = width
  exportCanvas.height = height
  
  // Draw background
  ctx.fillStyle = '#f0f0f0'
  ctx.fillRect(0, 0, width, height)
  
  // Draw grid if requested
  if (showGrid) {
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)'
    ctx.lineWidth = 1
    for (let x = 0; x <= mapStore.gridSize.width; x++) {
      ctx.beginPath()
      ctx.moveTo(x * tileSize, 0)
      ctx.lineTo(x * tileSize, height)
      ctx.stroke()
    }
    for (let y = 0; y <= mapStore.gridSize.height; y++) {
      ctx.beginPath()
      ctx.moveTo(0, y * tileSize)
      ctx.lineTo(width, y * tileSize)
      ctx.stroke()
    }
  }
  
  // Draw tiles and objects (simplified - would need to load images)
  // For now, just export the current canvas
  const dataURL = canvas.toDataURL(`image/${format}`, 0.95)
  
  // Download
  const link = document.createElement('a')
  link.download = `${mapStore.mapName || 'map'}_${new Date().toISOString().split('T')[0]}.${format}`
  link.href = dataURL
  link.click()
  
  alert('Export réussi!')
}
</script>

<style scoped>
.app-header {
  height: 60px;
  background: linear-gradient(135deg, var(--brown-dark) 0%, var(--gray-dark) 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  border-bottom: 2px solid var(--primary-color);
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  font-family: 'Creepster', cursive;
  font-size: 1.8rem;
  font-weight: normal;
  color: var(--primary-color);
}

.header-nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 0;
}

.nav-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-nav > .nav-group:not(:first-child) {
  padding-left: 12px;
  margin-left: 4px;
  border-left: 1px solid rgba(255, 255, 255, 0.22);
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

.header-btn {
  padding: 8px 16px;
  background: var(--brown-medium);
  color: white;
  border: 2px solid var(--brown-light);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  font-weight: 500;
}

.header-btn:hover {
  background: var(--brown-light);
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 2px 4px var(--shadow-accent);
}

.editor-tabs {
  display: flex;
  gap: 4px;
  align-items: center;
}

.nav-tab {
  padding: 6px 12px;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-size: 14px;
  border: 1px solid transparent;
}

.nav-tab:hover {
  background: rgba(255, 255, 255, 0.08);
}

.nav-tab-active {
  border-color: var(--primary-color);
  background: color-mix(in srgb, var(--primary-color) 22%, transparent);
  color: white;
}

.save-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--brown-light);
  color: rgba(255, 255, 255, 0.85);
  white-space: nowrap;
}

.save-status.dirty {
  border-color: var(--primary-color);
  color: #fff;
}

.header-btn.active {
  border-color: var(--primary-color);
  background: color-mix(in srgb, var(--primary-color) 35%, var(--brown-medium));
}

.header-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
}

.header-btn-icon {
  padding: 8px 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.25rem;
}

</style>
