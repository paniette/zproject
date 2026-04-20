<template>
  <div v-if="show" class="overlay" @click.self="emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>Versions locales</h3>
        <button type="button" class="close-btn" aria-label="Fermer" @click="emit('close')">×</button>
      </div>
      <p class="hint">
        Un instantané est ajouté après chaque sauvegarde réussie. La restauration remplace l’état courant (pensez à sauvegarder après si besoin).
      </p>
      <ul v-if="entries.length" class="list">
        <li v-for="(e, i) in entries" :key="e.ts + '-' + i">
          <div class="meta">
            <span class="label">{{ e.label }}</span>
            <span class="ts">{{ formatTs(e.ts) }}</span>
          </div>
          <button type="button" class="restore-btn" @click="onRestore(e)">Restaurer</button>
        </li>
      </ul>
      <p v-else class="empty">Aucune version enregistrée pour cette carte. Sauvegardez d’abord.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { listVersions } from '@/services/mapVersions'
import { useMapStore } from '@/stores/mapStore'

const props = defineProps({
  show: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])

const mapStore = useMapStore()

const entries = computed(() => {
  if (!props.show) return []
  const id = mapStore.currentMapId || 'draft'
  return listVersions(id)
})

function formatTs (ts) {
  try {
    return new Date(ts).toLocaleString('fr-FR')
  } catch {
    return String(ts)
  }
}

function onRestore (entry) {
  if (!entry?.data) return
  if (!confirm('Remplacer la carte courante par cette version ?')) return
  mapStore.loadMap(entry.data)
  mapStore.clearHistoryStacks()
  mapStore.isUnsaved = true
  emit('close')
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal {
  background: var(--brown-dark, #3d2817);
  color: #fff;
  border: 2px solid var(--primary-color, #e63946);
  border-radius: 8px;
  max-width: 520px;
  width: 100%;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--brown-light, #8b6f47);
}

.modal-header h3 {
  margin: 0;
  font-family: 'Creepster', cursive;
  color: var(--primary-color, #e63946);
}

.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.hint {
  margin: 0;
  padding: 12px 16px;
  font-size: 0.85rem;
  opacity: 0.9;
  line-height: 1.4;
}

.list {
  list-style: none;
  margin: 0;
  padding: 0 16px 16px;
  overflow-y: auto;
}

.list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.label {
  font-weight: 600;
  font-size: 0.9rem;
}

.ts {
  font-size: 0.75rem;
  opacity: 0.75;
}

.restore-btn {
  flex-shrink: 0;
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid var(--brown-light);
  background: var(--brown-medium);
  color: #fff;
  cursor: pointer;
  font-size: 0.85rem;
}

.restore-btn:hover {
  border-color: var(--primary-color);
}

.empty {
  padding: 16px;
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.85;
}
</style>
