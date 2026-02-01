<template>
  <div class="map-editor">
    <AppHeader />
    <div class="editor-container">
      <AssetPanel class="asset-panel" />
      <CanvasGrid class="canvas-grid" />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import AppHeader from './AppHeader.vue'
import AssetPanel from './AssetPanel.vue'
import CanvasGrid from './CanvasGrid.vue'
import { usePacksStore } from '@/stores/packsStore'
import { useAssetsStore } from '@/stores/assetsStore'
import api from '@/services/api'

const packsStore = usePacksStore()
const assetsStore = useAssetsStore()

const loadPacks = async () => {
  try {
    const response = await api.getPacks()
    if (response.data) {
      packsStore.setPacks(response.data)
    }
  } catch (error) {
    console.error('Error loading packs:', error)
  }
}

onMounted(async () => {
  // Load packs on mount
  await loadPacks()
  
  // Listen for pack refresh events (when new packs are uploaded)
  window.addEventListener('packs-refresh', loadPacks)
  
  return () => {
    window.removeEventListener('packs-refresh', loadPacks)
  }
})
</script>

<style scoped>
.map-editor {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.asset-panel {
  width: 25%;
  min-width: 250px;
  overflow-y: auto;
}

.canvas-grid {
  flex: 1;
  width: 75%;
  overflow: hidden;
}

@media (max-width: 768px) {
  .asset-panel {
    position: absolute;
    left: -100%;
    width: 80%;
    z-index: 100;
    background: white;
    transition: left 0.3s;
  }

  .asset-panel.open {
    left: 0;
  }
}
</style>
