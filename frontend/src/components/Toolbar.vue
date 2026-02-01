<template>
  <div class="toolbar">
    <div class="tool-group">
      <button
        v-for="tool in tools"
        :key="tool.id"
        :class="['tool-btn', { active: toolStore.activeTool === tool.id }]"
        @click="toolStore.setTool(tool.id)"
        :title="tool.label"
      >
        <span class="tool-icon">{{ tool.icon }}</span>
        <span class="tool-label">{{ tool.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useToolStore } from '@/stores/toolStore'

const toolStore = useToolStore()

const tools = [
  { id: 'place', label: 'Placer', icon: '📍' },
  { id: 'move', label: 'Déplacer', icon: '↔️' },
  { id: 'rotate', label: 'Rotater', icon: '🔄' },
  { id: 'delete', label: 'Supprimer', icon: '🗑️' }
]
</script>

<style scoped>
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: var(--brown-medium);
  color: white;
  border: 1px solid var(--brown-light);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  min-width: 60px;
}

.tool-btn:hover {
  background: var(--brown-light);
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.tool-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  box-shadow: 0 0 8px rgba(230, 57, 70, 0.5);
}

.tool-icon {
  font-size: 18px;
}

.tool-label {
  font-size: 10px;
  font-weight: 500;
}
</style>
