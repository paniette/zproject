<template>
  <div v-if="show" class="map-loader-overlay" @click.self="close">
    <div class="map-loader-modal">
      <div class="modal-header">
        <h2>Charger une carte</h2>
        <div class="header-controls">
          <div class="view-toggle">
            <button
              :class="['toggle-btn', viewMode === 'list' ? 'active' : '']"
              @click="viewMode = 'list'"
              title="Mode liste"
            >
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <rect x="1" y="3" width="16" height="2.5" rx="1" fill="currentColor"/>
                <rect x="1" y="7.75" width="16" height="2.5" rx="1" fill="currentColor"/>
                <rect x="1" y="12.5" width="16" height="2.5" rx="1" fill="currentColor"/>
              </svg>
            </button>
            <button
              :class="['toggle-btn', viewMode === 'grid' ? 'active' : '']"
              @click="viewMode = 'grid'"
              title="Mode miniatures"
            >
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <rect x="1" y="1" width="7" height="7" rx="1.5" fill="currentColor"/>
                <rect x="10" y="1" width="7" height="7" rx="1.5" fill="currentColor"/>
                <rect x="1" y="10" width="7" height="7" rx="1.5" fill="currentColor"/>
                <rect x="10" y="10" width="7" height="7" rx="1.5" fill="currentColor"/>
              </svg>
            </button>
          </div>
          <div class="search-box">
            <input v-model="searchQuery" type="text" placeholder="Rechercher..." />
          </div>
          <button @click="close" class="close-btn">×</button>
        </div>
      </div>

      <div class="modal-content">
        <!-- Mode liste -->
        <div v-if="viewMode === 'list'" class="maps-list">
          <div
            v-for="map in sortedFilteredMaps"
            :key="map.id"
            class="map-item"
          >
            <div class="map-info" @click="loadMap(map)">
              <h3>{{ map.name }}</h3>
              <p class="map-meta">Par {{ map.metadata?.author || 'temp' }}</p>
              <p class="map-date">{{ formatDate(map.metadata?.modified) }}</p>
            </div>
            <button @click.stop="deleteMap(map)" class="delete-btn" title="Supprimer">🗑️</button>
          </div>
          <p v-if="sortedFilteredMaps.length === 0" class="empty-state">Aucune carte trouvée.</p>
        </div>

        <!-- Mode miniatures -->
        <div v-else class="maps-grid">
          <div
            v-for="map in sortedFilteredMaps"
            :key="map.id"
            class="map-card"
            @click="loadMap(map)"
          >
            <div class="map-card-thumb">
              <img
                v-if="map.mission?.mapImageDataUrl"
                :src="map.mission.mapImageDataUrl"
                :alt="map.name"
                class="thumb-img"
              />
              <div v-else class="thumb-placeholder">
                <span class="thumb-initials">{{ initials(map.name) }}</span>
              </div>
              <button
                class="card-delete-btn"
                @click.stop="deleteMap(map)"
                title="Supprimer"
              >🗑️</button>
            </div>
            <div class="map-card-info">
              <p class="card-title">{{ map.name }}</p>
              <p class="card-meta">{{ map.metadata?.author || 'temp' }}</p>
              <p class="card-date">{{ formatDate(map.metadata?.modified) }}</p>
            </div>
          </div>
          <p v-if="sortedFilteredMaps.length === 0" class="empty-state">Aucune carte trouvée.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useUserStore } from '@/stores/userStore'
import api from '@/services/api'
import { formatDate } from '@/utils/mapUtils'

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['close', 'load'])

const mapStore = useMapStore()
const userStore = useUserStore()
const maps = ref([])
const searchQuery = ref('')
const viewMode = ref('grid')

const filteredMaps = computed(() => {
  if (!searchQuery.value) return maps.value
  const query = searchQuery.value.toLowerCase()
  return maps.value.filter(map =>
    map.name.toLowerCase().includes(query) ||
    (map.metadata?.author || '').toLowerCase().includes(query)
  )
})

const sortedFilteredMaps = computed(() => {
  return [...filteredMaps.value].sort((a, b) => {
    const dateA = a.metadata?.created || ''
    const dateB = b.metadata?.created || ''
    return dateB.localeCompare(dateA)
  })
})

function initials(name) {
  if (!name) return '?'
  return name
    .split(/\s+/)
    .slice(0, 2)
    .map(w => w[0]?.toUpperCase() || '')
    .join('')
}

const loadMaps = async () => {
  try {
    const response = await api.getUserMaps(userStore.currentUser)
    if (response.data && response.data.maps) {
      maps.value = response.data.maps
    }
  } catch (error) {
    console.error('Error loading maps:', error)
  }
}

const loadMap = async (map) => {
  try {
    const response = await api.getMap(userStore.currentUser, map.id)
    if (response.data) {
      mapStore.loadMap(response.data)
      emit('load', response.data)
      close()
    }
  } catch (error) {
    console.error('Error loading map:', error)
    alert('Erreur lors du chargement de la carte')
  }
}

const deleteMap = async (map) => {
  if (!confirm(`Êtes-vous sûr de vouloir supprimer la carte "${map.name}" ?`)) {
    return
  }
  try {
    await api.deleteMap(userStore.currentUser, map.id)
    await loadMaps()
  } catch (error) {
    console.error('Error deleting map:', error)
    alert('Erreur lors de la suppression de la carte')
  }
}

const close = () => {
  emit('close')
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    loadMaps()
  }
})

onMounted(() => {
  if (props.show) {
    loadMaps()
  }
})
</script>

<style scoped>
.map-loader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.map-loader-modal {
  background: linear-gradient(135deg, var(--gray-dark) 0%, var(--brown-dark) 100%);
  border-radius: 10px;
  width: 95vw;
  height: 90vh;
  display: flex;
  flex-direction: column;
  border: 2px solid var(--primary-color);
  box-shadow: 0 4px 24px rgba(0,0,0,0.6);
}

/* ─── Header ─── */
.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  gap: 12px;
}

.modal-header h2 {
  margin: 0;
  font-family: 'Creepster', cursive;
  color: var(--primary-color);
  white-space: nowrap;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  justify-content: flex-end;
}

/* ─── Toggle liste / grille ─── */
.view-toggle {
  display: flex;
  gap: 4px;
  background: rgba(0,0,0,0.3);
  padding: 3px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.1);
}

.toggle-btn {
  background: none;
  border: none;
  color: rgba(255,255,255,0.4);
  cursor: pointer;
  padding: 5px 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.toggle-btn:hover {
  color: rgba(255,255,255,0.8);
  background: rgba(255,255,255,0.08);
}

.toggle-btn.active {
  background: var(--primary-color);
  color: #fff;
}

/* ─── Search ─── */
.search-box {
  flex: 1;
  max-width: 320px;
}

.search-box input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 4px;
  font-size: 14px;
  background: rgba(0,0,0,0.3);
  color: #fff;
  box-sizing: border-box;
}

.search-box input::placeholder {
  color: rgba(255,255,255,0.4);
}

.close-btn {
  background: none;
  border: none;
  font-size: 26px;
  cursor: pointer;
  color: rgba(255,255,255,0.5);
  line-height: 1;
  padding: 0 4px;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #fff;
}

/* ─── Content ─── */
.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  text-align: center;
  color: rgba(255,255,255,0.4);
  margin-top: 40px;
  font-style: italic;
}

/* ─── Mode liste ─── */
.maps-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.map-item {
  padding: 14px 16px;
  border: 1px solid var(--brown-light);
  border-radius: 6px;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.07);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.map-item:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: var(--primary-color);
  transform: translateX(4px);
}

.map-info {
  flex: 1;
  cursor: pointer;
}

.map-info h3 {
  margin: 0 0 4px 0;
  color: var(--primary-color);
  font-family: 'Creepster', cursive;
}

.map-meta {
  margin: 3px 0;
  color: rgba(255,255,255,0.5);
  font-size: 0.9rem;
}

.map-date {
  margin: 3px 0 0 0;
  color: rgba(255,255,255,0.35);
  font-size: 0.8rem;
}

.delete-btn {
  background: var(--overlay-primary-weak);
  border: 1px solid var(--primary-color);
  border-radius: 4px;
  padding: 7px 11px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.delete-btn:hover {
  background: var(--overlay-primary-mid);
  transform: scale(1.1);
}

/* ─── Mode miniatures ─── */
.maps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.map-card {
  border: 1px solid var(--brown-light);
  border-radius: 8px;
  overflow: hidden;
  background: rgba(255,255,255,0.06);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.map-card:hover {
  border-color: var(--primary-color);
  background: rgba(255,255,255,0.12);
  transform: translateY(-3px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.5);
}

.map-card-thumb {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background: rgba(0,0,0,0.4);
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0,0,0,0.5) 0%, rgba(60,30,0,0.6) 100%);
}

.thumb-initials {
  font-family: 'Creepster', cursive;
  font-size: 2.8rem;
  color: var(--primary-color);
  opacity: 0.7;
  user-select: none;
}

.card-delete-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  background: rgba(0,0,0,0.65);
  border: 1px solid var(--primary-color);
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 14px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s, transform 0.2s;
}

.map-card:hover .card-delete-btn {
  opacity: 1;
}

.card-delete-btn:hover {
  transform: scale(1.15);
  background: rgba(180,0,0,0.5);
}

.map-card-info {
  padding: 10px 12px;
}

.card-title {
  margin: 0 0 3px 0;
  font-family: 'Creepster', cursive;
  color: var(--primary-color);
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  margin: 2px 0;
  color: rgba(255,255,255,0.5);
  font-size: 0.8rem;
}

.card-date {
  margin: 2px 0 0 0;
  color: rgba(255,255,255,0.35);
  font-size: 0.75rem;
}
</style>
