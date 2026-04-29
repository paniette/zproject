<template>
  <div id="asset-panel-region" class="asset-panel">
    <div class="panel-header">
      <h3>Packs & Assets</h3>
      <div
        class="game-type-filter"
        :class="{ 'has-selection': selectedGameType !== 'all' }"
        role="group"
        aria-label="Filtrer par type de jeu"
      >
        <button
          v-for="t in GAME_TYPES"
          :key="t.id"
          type="button"
          class="gt-btn"
          :class="{ active: selectedGameType === t.id }"
          :title="t.label"
          @click="selectedGameType = t.id"
        >
          <span v-if="t.id === 'all'">{{ t.label }}</span>
          <template v-else>
            <img class="gt-icon" :src="getGameTypeIcon(t.id)" :alt="t.label" />
            <span class="sr-only">{{ t.label }}</span>
          </template>
        </button>
      </div>
    </div>
    <div class="packs-list">
      <div v-for="pack in filteredPacks" :key="pack.id" class="pack-item">
        <div class="pack-header" @click="togglePack(pack.id)">
          <span class="pack-icon">{{ isPackOpen(pack.id) ? '▼' : '▶' }}</span>
          <span class="pack-name">{{ pack.name }}</span>
        </div>
        <div v-if="isPackOpen(pack.id)" class="pack-categories">
          <div v-for="category in getCategories(pack.id)" :key="category" class="category-item">
            <div class="category-header" @click="toggleCategory(pack.id, category)">
              <span class="category-icon">{{ isCategoryOpen(pack.id, category) ? '▼' : '▶' }}</span>
              <span class="category-name">{{ category }}</span>
            </div>
            <div v-if="isCategoryOpen(pack.id, category)" class="assets-grid">
              <div
                v-for="asset in getAssets(pack.id, category)"
                :key="asset.path"
                class="asset-item"
                :class="{
                  selected: isSelected(asset),
                  'asset-locked': isTilePairLocked(asset)
                }"
                :draggable="!isTilePairLocked(asset)"
                :title="isTilePairLocked(asset) ? 'Cette tuile (recto ou verso) est déjà sur la carte' : ''"
                @dragstart="handleDragStart($event, asset)"
                @click="selectAsset(asset)"
              >
                <img :src="getAssetThumbnail(asset)" :alt="asset.name" class="asset-thumbnail" />
                <span class="asset-name">{{ asset.name }}</span>
              </div>
              <button
                v-if="!config.staticMode"
                type="button"
                class="asset-item asset-item-add"
                aria-label="Ajouter un asset personnalisé dans cette catégorie"
                @click.stop="openInlineUploader(pack.id, category)"
              >
                <span class="asset-add-plus" aria-hidden="true">+</span>
                <span class="asset-name">Ajouter</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <PackUploader
      v-if="inlineUploaderOpen"
      :show="true"
      :pack-id="inlineUpload.packId"
      :category-preset="inlineUpload.category"
      @close="inlineUploaderOpen = false"
      @uploaded="onInlineUploaded"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePacksStore } from '@/stores/packsStore'
import { useAssetsStore } from '@/stores/assetsStore'
import { useMapStore } from '@/stores/mapStore'
import { useToolStore } from '@/stores/toolStore'
import { config } from '@/config'
import api from '@/services/api'
import PackUploader from './PackUploader.vue'
import { collectUsedTilePairKeys, isTilePairLocked as tilePairLocked } from '@/utils/tilePairs'
import { GAME_TYPES, loadPackGameTypeMap, getPackGameTypeFromPack } from '@/config/gameTypes'
import iconClassic from '@/assets/images/menu-setting-classic.jpg'
import iconModern from '@/assets/images/menu-setting-modern.jpg'
import iconFantasy from '@/assets/images/menu-setting-fantasy.jpg'
import iconWestern from '@/assets/images/menu-setting-western.jpg'
import iconScifi from '@/assets/images/menu-setting-scifi.jpg'
import iconNight from '@/assets/images/menu-setting-night.jpg'

const packsStore = usePacksStore()
const assetsStore = useAssetsStore()
const mapStore = useMapStore()
const toolStore = useToolStore()

function getGameTypeIcon (gameTypeId) {
  const iconById = {
    classic: iconClassic,
    modern: iconModern,
    fantasy: iconFantasy,
    western: iconWestern,
    scifi: iconScifi,
    night: iconNight
  }
  return iconById[gameTypeId] || ''
}

function maybeSwitchToPlaceTool () {
  if (typeof window === 'undefined') return
  // Sur tout appareil tactile (pointer: coarse), activer l'outil Placer dès qu'un asset est sélectionné,
  // quelle que soit la largeur de l'écran (le paysage sur grand téléphone dépasse 768px).
  if (!window.matchMedia('(pointer: coarse)').matches) return
  toolStore.setTool('place')
}

const usedTilePairKeys = computed(() => collectUsedTilePairKeys(mapStore.layers.tiles))

function isTilePairLocked (asset) {
  return tilePairLocked(asset.path, asset.category, usedTilePairKeys.value)
}

const openPacks = ref(new Set())
const openCategories = ref(new Map())

const packs = computed(() => packsStore.packs)
const selectedGameType = ref('all')
const packGameTypeMap = ref(loadPackGameTypeMap())

const filteredPacks = computed(() => {
  const list = packs.value || []
  if (selectedGameType.value === 'all') return list
  return list.filter((p) => getPackGameTypeFromPack(p, packGameTypeMap.value) === selectedGameType.value)
})

const inlineUploaderOpen = ref(false)
const inlineUpload = ref({ packId: '', category: '' })

const openInlineUploader = (packId, category) => {
  inlineUpload.value = { packId, category }
  inlineUploaderOpen.value = true
}

const onInlineUploaded = () => {
  inlineUploaderOpen.value = false
}

const refetchPackAssets = async (packId) => {
  try {
    const response = await api.getPackAssets(packId)
    if (response.data) {
      assetsStore.setAssets(packId, response.data)
    }
  } catch (error) {
    console.error('Error refreshing pack assets:', error)
  }
}

const onPackAssetsUpdated = (e) => {
  const packId = e.detail?.packId
  if (packId) refetchPackAssets(packId)
}

const onPackGameTypeUpdated = () => {
  packGameTypeMap.value = loadPackGameTypeMap()
}

const onAssetSelectedExternal = (e) => {
  if (e.detail == null) selectedAsset.value = null
}

onMounted(() => {
  window.addEventListener('pack-assets-updated', onPackAssetsUpdated)
  window.addEventListener('pack-game-type-updated', onPackGameTypeUpdated)
  window.addEventListener('asset-selected', onAssetSelectedExternal)
})

onUnmounted(() => {
  window.removeEventListener('pack-assets-updated', onPackAssetsUpdated)
  window.removeEventListener('pack-game-type-updated', onPackGameTypeUpdated)
  window.removeEventListener('asset-selected', onAssetSelectedExternal)
})

const togglePack = async (packId) => {
  if (openPacks.value.has(packId)) {
    openPacks.value.delete(packId)
  } else {
    openPacks.value.add(packId)
    // Load assets if not already loaded
    if (!assetsStore.assets[packId]) {
      try {
        const response = await api.getPackAssets(packId)
        if (response.data) {
          assetsStore.setAssets(packId, response.data)
        }
      } catch (error) {
        console.error('Error loading pack assets:', error)
      }
    }
  }
}

const isPackOpen = (packId) => {
  return openPacks.value.has(packId)
}

const toggleCategory = (packId, category) => {
  const key = `${packId}_${category}`
  if (openCategories.value.has(key)) {
    openCategories.value.delete(key)
  } else {
    openCategories.value.set(key, true)
  }
}

const isCategoryOpen = (packId, category) => {
  return openCategories.value.has(`${packId}_${category}`)
}

const getCategories = (packId) => {
  if (!assetsStore.assets[packId]) return []
  return Object.keys(assetsStore.assets[packId])
}

const getAssets = (packId, category) => {
  return assetsStore.getAssetsByCategory(packId, category)
}

const getAssetThumbnail = (asset) => {
  const baseUrl = import.meta.env.BASE_URL || ''
  // Try to get thumbnail, fallback to main image
  if (asset.thumbnail) {
    // Thumbnail path is already relative, use it directly
    const thumbPath = asset.thumbnail
    // Check if path starts with bgmapeditor_tiles or assets
    if (thumbPath.startsWith('bgmapeditor_tiles/') || thumbPath.startsWith('assets/')) {
      return `${baseUrl}${thumbPath}`
    }
    // Try both possible locations - first assets, then bgmapeditor_tiles
    return `${baseUrl}assets/${thumbPath}`
  }
  // Fallback to main image
  const mainPath = asset.path
  if (mainPath.startsWith('bgmapeditor_tiles/') || mainPath.startsWith('assets/')) {
    return `${baseUrl}${mainPath}`
  }
  return `${baseUrl}assets/${mainPath}`
}

const selectedAsset = ref(null)

const handleDragStart = (event, asset) => {
  if (isTilePairLocked(asset)) {
    event.preventDefault()
    return
  }
  event.dataTransfer.setData('application/json', JSON.stringify(asset))
  event.dataTransfer.effectAllowed = 'copy'
  selectedAsset.value = asset
}

const selectAsset = (asset) => {
  if (isTilePairLocked(asset)) return
  selectedAsset.value = asset
  // Dispatch event for CanvasGrid
  window.dispatchEvent(new CustomEvent('asset-selected', { detail: asset }))
  maybeSwitchToPlaceTool()
}

const isSelected = (asset) => {
  return selectedAsset.value && selectedAsset.value.path === asset.path
}
</script>

<style scoped>
.asset-panel {
  background: linear-gradient(180deg, var(--gray-dark) 0%, var(--brown-dark) 100%);
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 2px solid var(--primary-color);
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

.panel-header {
  padding: 15px;
  background: var(--brown-dark);
  color: white;
  border-bottom: 2px solid var(--primary-color);
}

.panel-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-family: 'Creepster', cursive;
  color: var(--primary-color);
}

.game-type-filter {
  margin-top: 10px;
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
  width: 100%;
  padding: 6px 0;
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
  line-height: 1;
  cursor: pointer;
  flex: 1 1 0;
  min-width: 52px;
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

@media (max-width: 520px) {
  .game-type-filter {
    overflow-x: auto;
    overflow-y: visible;
    -webkit-overflow-scrolling: touch;
  }

  .gt-btn {
    flex: 0 0 auto;
    width: 54px;
    min-width: 54px;
  }
}

.packs-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.pack-item {
  margin-bottom: 10px;
  background: white;
  border-radius: 4px;
  overflow: hidden;
}

.pack-header {
  padding: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--brown-medium);
  color: white;
  font-weight: 500;
  border-left: 3px solid var(--primary-color);
}

.pack-header:hover {
  background: var(--brown-light);
  border-left-color: var(--primary-color);
}

.pack-icon {
  font-size: 12px;
}

.pack-name {
  flex: 1;
}

.pack-categories {
  padding: 5px;
}

.category-item {
  margin-bottom: 5px;
}

.category-header {
  padding: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 4px;
  color: var(--dark-color);
  border: 1px solid var(--brown-light);
}

.category-header:hover {
  background: rgba(255, 255, 255, 1);
  border-color: var(--primary-color);
}

.category-icon {
  font-size: 10px;
  color: var(--dark-color);
}

.category-name {
  flex: 1;
  font-size: 0.9rem;
  color: var(--dark-color);
  font-weight: 500;
}

.assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
  padding: 8px;
}

.asset-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 5px;
  border: 1px solid var(--brown-light);
  border-radius: 4px;
  cursor: grab;
  background: rgba(255, 255, 255, 0.95);
  transition: all 0.2s;
}

.asset-item:hover {
  transform: scale(1.05);
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px var(--shadow-accent);
}

.asset-item.selected {
  border-color: var(--primary-color);
  background: var(--glow-soft);
  box-shadow: 0 0 8px var(--glow-strong);
}

.asset-item.asset-locked {
  opacity: 0.42;
  cursor: not-allowed;
  filter: grayscale(0.5);
  pointer-events: auto;
}

.asset-item.asset-locked:hover {
  transform: none;
  border-color: var(--brown-light);
  box-shadow: none;
}

.asset-item:active {
  cursor: grabbing;
}

.asset-item-add {
  cursor: pointer;
  border-style: dashed;
  border-color: var(--primary-color);
  background: rgba(255, 255, 255, 0.85);
  justify-content: center;
}

.asset-item-add:hover {
  background: rgba(230, 57, 70, 0.12);
  border-color: var(--primary-color);
}

.asset-item-add:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.asset-add-plus {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  margin-bottom: 5px;
  font-size: 2rem;
  font-weight: 300;
  line-height: 1;
  color: var(--primary-color);
  border-radius: 4px;
  background: rgba(230, 57, 70, 0.08);
}

.asset-thumbnail {
  width: 60px;
  height: 60px;
  object-fit: contain;
  margin-bottom: 5px;
}

.asset-name {
  font-size: 0.75rem;
  text-align: center;
  word-break: break-word;
  max-width: 100%;
  color: var(--dark-color);
  font-weight: 500;
}
</style>
