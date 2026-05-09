<template>
  <header class="app-header">
    <div class="header-content">
      <div class="header-left">
        <MissionSitesFlyout>{{ $t('header.appTitle') }}</MissionSitesFlyout>
        <span
          v-if="menuVis.saveStatus"
          class="save-status"
          :class="{ dirty: mapStore.isUnsaved }"
          :title="saveStatusTitle"
        >
          {{ mapStore.isUnsaved ? $t('header.modified') : $t('header.saved') }}
        </span>
      </div>
      <nav class="header-nav">
        <div class="nav-group">
          <div class="editor-tabs">
            <router-link to="/" class="nav-tab" active-class="nav-tab-active">{{ $t('header.tabMap') }}</router-link>
            <router-link to="/mission" class="nav-tab" active-class="nav-tab-active">{{ $t('header.tabMission') }}</router-link>
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
            :title="$t('header.undoTitle')"
            @click="mapStore.undo()"
          >
            <MenuGlyph name="undo" />
            <span class="sr-only">{{ $t('header.undo') }}</span>
          </button>
          <button
            type="button"
            class="header-btn header-btn-icon"
            :disabled="!mapStore.canRedo"
            :title="$t('header.redoTitle')"
            @click="mapStore.redo()"
          >
            <MenuGlyph name="redo" />
            <span class="sr-only">{{ $t('header.redo') }}</span>
          </button>
          <button
            v-if="menuVis.preview"
            type="button"
            class="header-btn"
            :class="{ active: mapStore.isPreviewMode }"
            :title="mapStore.isPreviewMode ? $t('header.exitPreviewTitle') : $t('header.previewTitle')"
            @click="togglePreview"
          >
            {{ mapStore.isPreviewMode ? $t('header.exitPreview') : $t('header.preview') }}
          </button>
          <button type="button" class="header-btn header-btn-icon" :title="$t('header.loadMap')" @click="openMapLoader">
            <MenuGlyph name="load" />
            <span class="sr-only">{{ $t('header.loadMap') }}</span>
          </button>
          <button type="button" class="header-btn header-btn-icon" :title="$t('header.saveMap')" @click="saveMap">
            <MenuGlyph name="save" />
            <span class="sr-only">{{ $t('header.saveMap') }}</span>
          </button>
        </div>

        <div v-if="showExportsGroup" class="nav-group">
          <button
            v-if="menuVis.exportJson"
            type="button"
            class="header-btn"
            :title="$t('header.exportJson')"
            @click="exportScenarioJson"
          >
            JSON
          </button>
          <button
            v-if="menuVis.exportXml"
            type="button"
            class="header-btn"
            :title="$t('header.exportXml')"
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
            {{ $t('header.versions') }}
          </button>
        </div>

        <div class="nav-group">
          <button
            type="button"
            class="header-btn header-btn-icon"
            :title="$t('header.exportPng')"
            @click="exportMap"
          >
            <MenuGlyph name="exportImage" />
            <span class="sr-only">{{ $t('header.exportPngSr') }}</span>
          </button>
        </div>

        <div v-if="menuVis.uploadZip || menuVis.uploadElement" class="nav-group">
          <button v-if="menuVis.uploadZip" type="button" class="header-btn" @click="openPackZipUploader">{{ $t('header.uploadZip') }}</button>
          <button v-if="menuVis.uploadElement" type="button" class="header-btn" @click="openPackUploader">{{ $t('header.uploadElement') }}</button>
        </div>

        <div class="nav-group nav-group-donate">
          <button
            type="button"
            class="header-btn header-btn-icon donate-btn-header"
            :title="$t('donate.buttonTitle')"
            @click="showDonateModal = true"
          >
            <MenuGlyph name="heart" class="donate-heart-glyph" />
            <span class="sr-only">{{ $t('donate.buttonTitle') }}</span>
          </button>
        </div>

        <div v-if="menuVis.langToggle" class="nav-group">
          <select
            class="header-btn lang-select"
            :value="langStore.locale"
            :aria-label="'Langue / Language'"
            @change="langStore.setLocale($event.target.value)"
          >
            <option v-for="loc in supportedLocales" :key="loc" :value="loc">
              {{ $t('lang.' + loc) }}
            </option>
          </select>
        </div>
      </nav>
    </div>
    <MapLoader :show="showMapLoader" @close="closeMapLoader" @load="handleMapLoad" />
    <PackZipUploader v-if="showPackZipUploader" @close="closePackZipUploader" />
    <PackUploader v-if="showPackUploader" @close="closePackUploader" />
    <MapVersionsModal :show="showVersionsModal" @close="showVersionsModal = false" />
    <DonateModal :show="showDonateModal" @close="showDonateModal = false" />
    <SaveMapModal
      :show="showSaveModal"
      :initial-name="saveModalInitialName"
      @close="showSaveModal = false"
      @submit="handleSaveNameSubmit"
    />
  </header>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLangStore } from '@/stores/langStore'
import { SUPPORTED_LOCALES } from '@/i18n'
import ThemeSelector from './ThemeSelector.vue'
import UserSelector from './UserSelector.vue'
import MapLoader from './MapLoader.vue'
import PackZipUploader from './PackZipUploader.vue'
import PackUploader from './PackUploader.vue'
import MapVersionsModal from './MapVersionsModal.vue'
import MenuGlyph from './MenuGlyph.vue'
import SaveMapModal from './SaveMapModal.vue'
import DonateModal from './DonateModal.vue'
import MissionSitesFlyout from './MissionSitesFlyout.vue'
import { useMapStore } from '@/stores/mapStore'
import { useUserStore } from '@/stores/userStore'
import { config } from '@/config'
import api from '@/services/api'
import { requestCanvasExportWithoutGrid } from '@/services/canvasExport'
import { pushVersion } from '@/services/mapVersions'
import { mapPayloadToXml } from '@/utils/mapExportXml'
import { getEditorMenuVisibility } from '@/config/editorMenu'

const { t } = useI18n()
const langStore = useLangStore()
const supportedLocales = SUPPORTED_LOCALES
const mapStore = useMapStore()
const userStore = useUserStore()

const showMapLoader = ref(false)
const showPackZipUploader = ref(false)
const showPackUploader = ref(false)
const showVersionsModal = ref(false)
const showSaveModal = ref(false)
const showDonateModal = ref(false)
const pendingSave = ref(false)

const isUnsaved = ref(true)

const saveStatusTitle = computed(() =>
  mapStore.isUnsaved
    ? t('header.saveStatusUnsaved')
    : t('header.saveStatusSaved')
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

const saveModalInitialName = computed(() => {
  const name = String(mapStore.mapName || '').trim()
  return name
})

function ensureMapNameForSave () {
  const name = String(mapStore.mapName || '').trim()
  const hasRealName = name.length > 0 && (mapStore.currentMapId || true)

  if (hasRealName) return true
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
      },
      mission: JSON.parse(JSON.stringify(mapStore.mission))
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
      pushVersion(mapStore.currentMapId || 'draft', t('map.versionLabel'), snapshot)
    } catch (verErr) {
      console.warn('Version locale non enregistrée', verErr)
    }
    alert(t('header.saveSuccess') + (config.staticMode ? t('header.saveSuccessLocal') : ''))
  } catch (error) {
    console.error('Error saving map:', error)
    alert(t('header.saveError', { msg: error.response?.data?.error || error.message }))
  }
}

function mapNameToExportPngFilename () {
  let raw = String(mapStore.mapName || '').trim()
  if (!raw) raw = 'carte'
  const ascii = raw.normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
  const slug = ascii.replace(/[^a-zA-Z0-9]+/g, '').slice(0, 120) || 'carte'
  return `${slug}.png`
}

function isCoarseOrMobileUa () {
  if (typeof window === 'undefined') return false
  if (window.matchMedia('(pointer: coarse)').matches) return true
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent || '')
}

const exportMap = async () => {
  const mime = 'image/png'
  const quality = 0.92
  try {
    const dataURL = await requestCanvasExportWithoutGrid({ mimeType: mime, quality })
    const filename = mapNameToExportPngFilename()

    if (isCoarseOrMobileUa()) {
      const blob = await (await fetch(dataURL)).blob()
      try {
        const file = new File([blob], filename, { type: 'image/png' })
        if (typeof navigator !== 'undefined' && navigator.share && typeof navigator.canShare === 'function' && navigator.canShare({ files: [file] })) {
          await navigator.share({ files: [file], title: filename })
          return
        }
      } catch (shareErr) {
        if (shareErr && shareErr.name === 'AbortError') return
        console.warn('Partage PNG indisponible', shareErr)
      }
      const blobUrl = URL.createObjectURL(blob)
      const w = window.open(blobUrl, '_blank', 'noopener,noreferrer')
      if (w) {
        setTimeout(() => URL.revokeObjectURL(blobUrl), 120000)
        return
      }
      URL.revokeObjectURL(blobUrl)
    }

    const link = document.createElement('a')
    link.download = filename
    link.href = dataURL
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (e) {
    console.error(e)
    alert(t('header.exportError', { msg: e?.message || e }))
  }
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

.lang-select {
  min-width: 3.2rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  font-size: 13px;
  cursor: pointer;
  background-color: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  color: inherit;
  padding: 2px 4px;
  appearance: none;
  -webkit-appearance: none;
  text-align: center;
}

.lang-select:hover {
  background-color: rgba(255, 255, 255, 0.12);
}

.lang-select option {
  background-color: #2a2a2a;
  color: #fff;
}

.nav-group-donate {
  margin-left: 4px;
}

.donate-btn-header {
  border-color: rgba(200, 80, 80, 0.35);
  background: rgba(180, 50, 50, 0.12);
  transition: all 0.2s;
}

.donate-btn-header:hover {
  border-color: rgba(220, 80, 80, 0.7);
  background: rgba(180, 50, 50, 0.28);
  box-shadow: 0 0 10px rgba(200, 60, 60, 0.3);
  transform: translateY(-2px);
}

.donate-heart-glyph {
  color: #e05555;
  filter: drop-shadow(0 0 4px rgba(220, 70, 70, 0.5));
}

@media (max-width: 768px) {
  .app-header {
    height: auto;
    min-height: 52px;
    padding: 8px 12px;
    padding-left: max(12px, env(safe-area-inset-left, 0px));
    padding-right: max(12px, env(safe-area-inset-right, 0px));
    padding-top: max(8px, env(safe-area-inset-top, 0px));
  }

  .header-content {
    flex-wrap: wrap;
    gap: 8px;
    align-items: flex-start;
  }

  .header-left {
    flex-wrap: wrap;
    gap: 8px;
    min-width: 0;
  }

  .header-nav {
    width: 100%;
    justify-content: flex-start;
    gap: 6px 4px;
  }

  .header-nav > .nav-group:not(:first-child) {
    padding-left: 8px;
    margin-left: 2px;
  }

  .header-btn {
    padding: 10px 12px;
    min-height: 44px;
    font-size: 13px;
  }

  .header-btn-icon {
    min-width: 44px;
    min-height: 44px;
    padding: 10px;
  }

  .nav-tab {
    padding: 10px 12px;
    min-height: 44px;
    display: inline-flex;
    align-items: center;
  }

  .save-status {
    font-size: 11px;
  }
}
</style>
