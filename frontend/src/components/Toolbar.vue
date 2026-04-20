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
}

.tool-group {
  display: flex;
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

.tool-icon {
  font-size: 1.35rem;
  line-height: 1;
}
</style>
