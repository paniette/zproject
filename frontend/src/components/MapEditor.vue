<template>
  <div class="map-editor">
    <div class="editor-container">
      <div
        v-if="assetsDrawerOpen"
        class="assets-overlay"
        aria-hidden="true"
        @click="assetsDrawerOpen = false"
      />
      <AssetPanel
        class="asset-panel"
        :class="{ open: assetsDrawerOpen }"
      />
      <CanvasGrid class="canvas-grid" />
      <PropertyPanel v-if="menuVis.propertyPanel" class="property-panel" />
      <button
        type="button"
        class="fab-assets"
        :aria-expanded="assetsDrawerOpen"
        aria-controls="asset-panel-region"
        @click="toggleAssetsDrawer"
      >
        Packs &amp; Assets
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import AssetPanel from './AssetPanel.vue'
import CanvasGrid from './CanvasGrid.vue'
import PropertyPanel from './PropertyPanel.vue'
import { usePacksStore } from '@/stores/packsStore'
import { useAssetsStore } from '@/stores/assetsStore'
import { getEditorMenuVisibility } from '@/config/editorMenu'
import api from '@/services/api'

const packsStore = usePacksStore()
const assetsStore = useAssetsStore()

const menuVis = computed(() => getEditorMenuVisibility())

const assetsDrawerOpen = ref(false)

const MOBILE_DRAWER_MQ = '(max-width: 768px)'

function isMobileDrawerLayout () {
  return typeof window !== 'undefined' && window.matchMedia(MOBILE_DRAWER_MQ).matches
}

function toggleAssetsDrawer () {
  assetsDrawerOpen.value = !assetsDrawerOpen.value
}

function onAssetSelected (e) {
  if (!isMobileDrawerLayout()) return
  if (e.detail != null) assetsDrawerOpen.value = false
}

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
  await loadPacks()
  window.addEventListener('packs-refresh', loadPacks)
  window.addEventListener('asset-selected', onAssetSelected)
})

onUnmounted(() => {
  window.removeEventListener('packs-refresh', loadPacks)
  window.removeEventListener('asset-selected', onAssetSelected)
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
  position: relative;
}

.asset-panel {
  width: 25%;
  min-width: 250px;
  overflow-y: auto;
}

.canvas-grid {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.property-panel {
  flex-shrink: 0;
}

.assets-overlay {
  display: none;
}

.fab-assets {
  display: none;
}

@media (max-width: 768px) {
  .assets-overlay {
    display: block;
    position: absolute;
    inset: 0;
    z-index: 95;
    background: rgba(0, 0, 0, 0.45);
  }

  .asset-panel {
    position: absolute;
    left: -100%;
    top: 0;
    bottom: 0;
    width: min(86vw, 360px);
    max-width: 100%;
    z-index: 100;
    min-width: 0;
    transition: left 0.25s ease;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.35);
    padding-bottom: env(safe-area-inset-bottom, 0px);
  }

  .asset-panel.open {
    left: 0;
  }

  .fab-assets {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    bottom: calc(12px + env(safe-area-inset-bottom, 0px));
    left: max(12px, env(safe-area-inset-left, 0px));
    z-index: 110;
    padding: 12px 16px;
    min-height: 44px;
    border: 2px solid var(--brown-light, #8b6f47);
    border-radius: 8px;
    background: linear-gradient(135deg, var(--brown-dark, #3d2817), var(--gray-dark, #2c2c2c));
    color: #fff;
    font-size: 14px;
    font-weight: 600;
    font-family: Roboto, system-ui, sans-serif;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
    cursor: pointer;
  }

  .fab-assets:active {
    transform: scale(0.98);
  }
}
</style>
