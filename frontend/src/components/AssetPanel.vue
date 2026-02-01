<template>
  <div class="asset-panel">
    <div class="panel-header">
      <h3>Packs & Assets</h3>
    </div>
    <div class="packs-list">
      <div v-for="pack in packs" :key="pack.id" class="pack-item">
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
                :class="{ selected: isSelected(asset) }"
                draggable="true"
                @dragstart="handleDragStart($event, asset)"
                @click="selectAsset(asset)"
              >
                <img :src="getAssetThumbnail(asset)" :alt="asset.name" class="asset-thumbnail" />
                <span class="asset-name">{{ asset.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePacksStore } from '@/stores/packsStore'
import { useAssetsStore } from '@/stores/assetsStore'
import api from '@/services/api'

const packsStore = usePacksStore()
const assetsStore = useAssetsStore()

const openPacks = ref(new Set())
const openCategories = ref(new Map())

const packs = computed(() => packsStore.packs)

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
  // Try to get thumbnail, fallback to main image
  if (asset.thumbnail) {
    // Thumbnail path is already relative, use it directly
    const thumbPath = asset.thumbnail
    // Check if path starts with bgmapeditor_tiles or assets
    if (thumbPath.startsWith('bgmapeditor_tiles/') || thumbPath.startsWith('assets/')) {
      return `/${thumbPath}`
    }
    // Try both possible locations - first assets, then bgmapeditor_tiles
    return `/assets/${thumbPath}`
  }
  // Fallback to main image
  const mainPath = asset.path
  if (mainPath.startsWith('bgmapeditor_tiles/') || mainPath.startsWith('assets/')) {
    return `/${mainPath}`
  }
  return `/assets/${mainPath}`
}

const selectedAsset = ref(null)

const handleDragStart = (event, asset) => {
  event.dataTransfer.setData('application/json', JSON.stringify(asset))
  event.dataTransfer.effectAllowed = 'copy'
  selectedAsset.value = asset
}

const selectAsset = (asset) => {
  selectedAsset.value = asset
  // Dispatch event for CanvasGrid
  window.dispatchEvent(new CustomEvent('asset-selected', { detail: asset }))
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
  box-shadow: 0 2px 8px rgba(230, 57, 70, 0.3);
}

.asset-item.selected {
  border-color: var(--primary-color);
  background: rgba(230, 57, 70, 0.1);
  box-shadow: 0 0 8px rgba(230, 57, 70, 0.5);
}

.asset-item:active {
  cursor: grabbing;
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
