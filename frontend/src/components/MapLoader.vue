<template>
  <div v-if="show" class="map-loader-overlay" @click.self="close">
    <div class="map-loader-modal">
      <div class="modal-header">
        <h2>Charger une carte</h2>
        <button @click="close" class="close-btn">×</button>
      </div>
      <div class="modal-content">
        <div class="search-box">
          <input v-model="searchQuery" type="text" placeholder="Rechercher..." />
        </div>
        <div class="maps-list">
          <div
            v-for="map in filteredMaps"
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

const filteredMaps = computed(() => {
  if (!searchQuery.value) return maps.value
  const query = searchQuery.value.toLowerCase()
  return maps.value.filter(map =>
    map.name.toLowerCase().includes(query) ||
    (map.metadata?.author || '').toLowerCase().includes(query)
  )
})

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
    // Recharger la liste des cartes
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
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.map-loader-modal {
  background: linear-gradient(135deg, var(--gray-dark) 0%, var(--brown-dark) 100%);
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  border: 2px solid var(--primary-color);
  box-shadow: 0 4px 16px rgba(0,0,0,0.5);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-family: 'Creepster', cursive;
  color: var(--primary-color);
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #000;
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.search-box {
  margin-bottom: 20px;
}

.search-box input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.maps-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.map-item {
  padding: 15px;
  border: 1px solid var(--brown-light);
  border-radius: 4px;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.map-item:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: var(--primary-color);
  transform: translateX(5px);
}

.map-info {
  flex: 1;
  cursor: pointer;
}

.delete-btn {
  background: rgba(230, 57, 70, 0.2);
  border: 1px solid var(--primary-color);
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.delete-btn:hover {
  background: rgba(230, 57, 70, 0.4);
  transform: scale(1.1);
}

.map-info h3 {
  margin: 0 0 5px 0;
  color: var(--primary-color);
  font-family: 'Creepster', cursive;
}

.map-meta {
  margin: 5px 0;
  color: #666;
  font-size: 0.9rem;
}

.map-date {
  margin: 5px 0 0 0;
  color: #999;
  font-size: 0.8rem;
}
</style>
