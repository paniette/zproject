<template>
  <header class="app-header">
    <div class="header-content">
      <div class="header-left">
        <div class="logo">Zombicide Editor</div>
        <input
          v-model="mapNameInput"
          @blur="updateMapName"
          @keyup.enter="updateMapName"
          class="map-name-input"
          :placeholder="mapNamePlaceholder"
        />
      </div>
      <nav class="header-nav">
        <UserSelector />
        <span class="separator">|</span>
        <button @click="openMapLoader" class="header-btn">Charger</button>
        <button @click="saveMap" class="header-btn">Sauvegarder</button>
        <span class="separator">|</span>
        <button @click="exportMap" class="header-btn">Exporter</button>
        <span v-if="!config.staticMode" class="separator">|</span>
        <button v-if="!config.staticMode" @click="openPackZipUploader" class="header-btn">Upload Pack ZIP</button>
        <button v-if="!config.staticMode" @click="openPackUploader" class="header-btn">Upload Pack Element</button>
      </nav>
    </div>
    <MapLoader :show="showMapLoader" @close="closeMapLoader" @load="handleMapLoad" />
    <PackZipUploader v-if="showPackZipUploader" @close="closePackZipUploader" />
    <PackUploader v-if="showPackUploader" @close="closePackUploader" />
  </header>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import UserSelector from './UserSelector.vue'
import MapLoader from './MapLoader.vue'
import PackZipUploader from './PackZipUploader.vue'
import PackUploader from './PackUploader.vue'
import { useMapStore } from '@/stores/mapStore'
import { useUserStore } from '@/stores/userStore'
import { config } from '@/config'
import api from '@/services/api'

const mapStore = useMapStore()
const userStore = useUserStore()

const showMapLoader = ref(false)
const showPackZipUploader = ref(false)
const showPackUploader = ref(false)

const mapNameInput = ref('')
const isUnsaved = ref(true)

const mapNamePlaceholder = computed(() => {
  if (isUnsaved.value && !mapStore.currentMapId) {
    return 'untitled/unsaved'
  }
  return mapStore.mapName || 'untitled'
})

watch(() => mapStore.mapName, (newName) => {
  if (newName) {
    mapNameInput.value = newName
  }
})

watch(() => mapStore.currentMapId, (newId) => {
  if (newId) {
    isUnsaved.value = false
  } else {
    isUnsaved.value = true
  }
})

const updateMapName = () => {
  if (mapNameInput.value.trim()) {
    mapStore.mapName = mapNameInput.value.trim()
  }
}

const openPackUploader = () => {
  showPackUploader.value = true
}

const closePackUploader = () => {
  showPackUploader.value = false
}

const openMapLoader = () => {
  showMapLoader.value = true
}

const closeMapLoader = () => {
  showMapLoader.value = false
}

const openPackZipUploader = () => {
  showPackZipUploader.value = true
}

const closePackZipUploader = () => {
  showPackZipUploader.value = false
}

const handleMapLoad = (mapData) => {
  mapStore.loadMap(mapData)
  mapNameInput.value = mapData.name || 'untitled'
  isUnsaved.value = false
  closeMapLoader()
}

// Keyboard shortcut for save
onMounted(() => {
  // Initialize map name input
  if (mapStore.mapName && mapStore.currentMapId) {
    mapNameInput.value = mapStore.mapName
    isUnsaved.value = false
  } else {
    mapNameInput.value = ''
    isUnsaved.value = true
  }
  
  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault()
      saveMap()
    }
  }
  window.addEventListener('keydown', handleKeyDown)
  
  return () => {
    window.removeEventListener('keydown', handleKeyDown)
  }
})

const saveMap = async () => {
  try {
    // Use name from input field
    if (mapNameInput.value.trim()) {
      mapStore.mapName = mapNameInput.value.trim()
    }
    
    // If new map and no name, ask for name
    if (!mapStore.currentMapId && !mapStore.mapName) {
      const name = prompt('Nom de la carte:', 'untitled')
      if (!name) return
      mapStore.mapName = name
      mapNameInput.value = name
    }
    
    const mapData = {
      name: mapStore.mapName,
      pack: mapStore.currentPack,
      grid: {
        width: mapStore.gridSize.width,
        height: mapStore.gridSize.height,
        tileSize: mapStore.tileSize
      },
      layers: mapStore.layers,
      gridOffsetX: mapStore.gridOffsetX,
      gridOffsetY: mapStore.gridOffsetY,
      metadata: {
        created: mapStore.currentMapId ? undefined : new Date().toISOString(),
        modified: new Date().toISOString(),
        author: userStore.currentUser
      }
    }

    if (mapStore.currentMapId) {
      const response = await api.updateMap(userStore.currentUser, mapStore.currentMapId, mapData)
      mapStore.currentMapId = response.data.id
    } else {
      const response = await api.createMap(userStore.currentUser, mapData)
      mapStore.currentMapId = response.data.id
      isUnsaved.value = false // Remove unsaved status after first save
      mapStore.isUnsaved = false
    }
    mapNameInput.value = mapStore.mapName
    alert('Carte sauvegardée avec succès!' + (config.staticMode ? ' (sauvegardée localement)' : ''))
  } catch (error) {
    console.error('Error saving map:', error)
    alert('Erreur lors de la sauvegarde: ' + (error.response?.data?.error || error.message))
  }
}

const exportMap = () => {
  // Show export modal
  const format = prompt('Format (png/jpeg):', 'png')
  if (!format) return
  
  const showGrid = confirm('Afficher la grille?')
  const resolution = prompt('Résolution (1=standard, 2=2x, 4=4x):', '1')
  const scale = parseFloat(resolution) || 1
  
  // Get canvas from CanvasGrid
  const canvas = document.querySelector('canvas')
  if (!canvas) {
    alert('Canvas non trouvé')
    return
  }
  
  // Create export canvas
  const exportCanvas = document.createElement('canvas')
  const ctx = exportCanvas.getContext('2d')
  const tileSize = mapStore.tileSize * scale
  const width = mapStore.gridSize.width * tileSize
  const height = mapStore.gridSize.height * tileSize
  
  exportCanvas.width = width
  exportCanvas.height = height
  
  // Draw background
  ctx.fillStyle = '#f0f0f0'
  ctx.fillRect(0, 0, width, height)
  
  // Draw grid if requested
  if (showGrid) {
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)'
    ctx.lineWidth = 1
    for (let x = 0; x <= mapStore.gridSize.width; x++) {
      ctx.beginPath()
      ctx.moveTo(x * tileSize, 0)
      ctx.lineTo(x * tileSize, height)
      ctx.stroke()
    }
    for (let y = 0; y <= mapStore.gridSize.height; y++) {
      ctx.beginPath()
      ctx.moveTo(0, y * tileSize)
      ctx.lineTo(width, y * tileSize)
      ctx.stroke()
    }
  }
  
  // Draw tiles and objects (simplified - would need to load images)
  // For now, just export the current canvas
  const dataURL = canvas.toDataURL(`image/${format}`, 0.95)
  
  // Download
  const link = document.createElement('a')
  link.download = `${mapStore.mapName || 'map'}_${new Date().toISOString().split('T')[0]}.${format}`
  link.href = dataURL
  link.click()
  
  alert('Export réussi!')
}
</script>

<style scoped>
.app-header {
  height: 60px;
  background: linear-gradient(135deg, var(--brown-dark) 0%, var(--gray-dark) 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  border-bottom: 2px solid var(--primary-color);
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.map-name-input {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid var(--brown-light);
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
  transition: all 0.2s;
}

.map-name-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.2);
  border-color: var(--primary-color);
}

.map-name-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.logo {
  font-family: 'Creepster', cursive;
  font-size: 1.8rem;
  font-weight: normal;
  color: #e63946;
}

.header-nav {
  display: flex;
  gap: 10px;
  align-items: center;
}

.separator {
  color: var(--brown-light);
  font-size: 18px;
  margin: 0 5px;
  user-select: none;
}

.header-btn {
  padding: 8px 16px;
  background: var(--brown-medium);
  color: white;
  border: 2px solid var(--brown-light);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  font-weight: 500;
}

.header-btn:hover {
  background: var(--brown-light);
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(230, 57, 70, 0.3);
}
</style>
