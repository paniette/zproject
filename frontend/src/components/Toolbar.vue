<template>
  <div class="toolbar" :class="{ 'toolbar-preview': mapStore.isPreviewMode }">
    <div class="tool-group">
      <button
        v-for="tool in tools"
        :key="tool.id"
        :class="['tool-btn', { active: toolStore.activeTool === tool.id }]"
        :disabled="mapStore.isPreviewMode"
        @click="toolStore.setTool(tool.id)"
        :title="tool.label"
      >
        <span class="tool-icon" aria-hidden="true">{{ tool.icon }}</span>
      </button>
      <button
        v-if="toolStore.selectedObject"
        type="button"
        class="tool-btn tool-btn-rotate-selection"
        :disabled="mapStore.isPreviewMode"
        title="Pivoter la sélection (+90°, équivalent clic droit)"
        @click="rotateSelection"
      >
        <span class="tool-icon" aria-hidden="true">↻</span>
        <span class="sr-only">Pivoter la sélection</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useToolStore } from '@/stores/toolStore'
import { useMapStore } from '@/stores/mapStore'

const toolStore = useToolStore()
const mapStore = useMapStore()

const tools = [
  { id: 'place', label: 'Placer', icon: '📍' },
  { id: 'move', label: 'Déplacer', icon: '↔️' },
  { id: 'rotate', label: 'Rotater', icon: '🔄' },
  { id: 'delete', label: 'Supprimer', icon: '🗑️' }
]

function rotateSelection () {
  const id = toolStore.selectedObject
  if (!id) return
  const obj = mapStore.layers.objects.find((o) => o.id === id)
  const tile = obj ? null : mapStore.layers.tiles.find((t) => t.id === id)
  if (obj) {
    mapStore.updateObject(obj.id, { rotation: (obj.rotation + 90) % 360 })
  } else if (tile) {
    mapStore.updateTile(tile.id, { rotation: (tile.rotation + 90) % 360 })
  }
}
</script>

<style scoped>
.toolbar-preview {
  opacity: 0.45;
  pointer-events: none;
}

.toolbar {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 100;
  background: rgba(45, 45, 45, 0.95);
  padding: 8px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.5);
  border: 1px solid var(--primary-color);
  max-width: calc(100vw - 24px);
}

.tool-group {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tool-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 10px;
  background: var(--brown-medium);
  color: white;
  border: 1px solid var(--brown-light);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  min-width: 2.5rem;
}

.tool-btn:hover {
  background: var(--brown-light);
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.tool-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  box-shadow: 0 0 8px var(--glow-strong);
}

.tool-btn-rotate-selection {
  border-color: color-mix(in srgb, var(--primary-color) 55%, var(--brown-light));
}

.tool-icon {
  font-size: 1.35rem;
  line-height: 1;
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

@media (max-width: 768px) {
  .toolbar {
    top: max(8px, env(safe-area-inset-top, 0px));
    left: max(8px, env(safe-area-inset-left, 0px));
    padding: 10px;
  }

  .tool-btn {
    min-width: 2.75rem;
    min-height: 44px;
    padding: 10px 12px;
  }

  .tool-btn:hover {
    transform: none;
  }

  .tool-icon {
    font-size: 1.45rem;
  }
}
</style>
