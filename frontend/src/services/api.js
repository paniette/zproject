import axios from 'axios'
import { config } from '@/config'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Static packs index cache
let staticPacksIndex = null
let staticMapsIndex = null

// Load static packs index
async function loadStaticPacksIndex() {
  if (staticPacksIndex) return staticPacksIndex
  
  try {
    const response = await fetch(config.packsIndexPath)
    staticPacksIndex = await response.json()
    return staticPacksIndex
  } catch (error) {
    console.error('Error loading static packs index:', error)
    return { packs: [] }
  }
}

// Load static maps index
async function loadStaticMapsIndex() {
  if (staticMapsIndex) return staticMapsIndex
  
  try {
    const response = await fetch('/maps-index.json')
    staticMapsIndex = await response.json()
    return staticMapsIndex
  } catch (error) {
    console.error('Error loading static maps index:', error)
    return { maps: [] }
  }
}

export default {
  // Packs
  async getPacks() {
    if (config.staticMode) {
      const index = await loadStaticPacksIndex()
      // Return in the same format as the API
      return {
        data: index.packs.map(pack => ({
          id: pack.id,
          name: pack.name,
          image: pack.image,
          align: pack.align
        }))
      }
    }
    return api.get('/packs/')
  },

  async getPack(packId) {
    if (config.staticMode) {
      const index = await loadStaticPacksIndex()
      const pack = index.packs.find(p => p.id === packId)
      return { data: pack || null }
    }
    return api.get(`/packs/${packId}/`)
  },

  async getPackAssets(packId) {
    if (config.staticMode) {
      const index = await loadStaticPacksIndex()
      const pack = index.packs.find(p => p.id === packId)
      return { data: pack?.assets || {} }
    }
    return api.get(`/packs/${packId}/assets/`)
  },

  // Assets
  getAsset(assetPath) {
    // Handle both /assets/ and /bgmapeditor_tiles/ paths
    if (assetPath.startsWith('assets/') || assetPath.startsWith('bgmapeditor_tiles/')) {
      return `/${assetPath}`
    }
    return `/assets/${assetPath}`
  },

  // Users
  getUsers() {
    return api.get('/users/')
  },

  // Maps
  async getUserMaps(username) {
    if (config.staticMode) {
      // Load from static index first
      const index = await loadStaticMapsIndex()
      const staticMaps = index.maps.filter(m => m.metadata?.author === username)
      
      // Also load from localStorage
      const { localStorageService } = await import('./localStorage')
      const localMaps = localStorageService.getUserMaps(username)
      
      // Merge and deduplicate (localStorage takes precedence)
      const allMaps = [...staticMaps]
      for (const localMap of localMaps) {
        if (!allMaps.find(m => m.id === localMap.id)) {
          allMaps.push(localMap)
        }
      }
      
      return { data: { maps: allMaps } }
    }
    return api.get(`/users/${username}/maps/`)
  },

  async createMap(username, mapData) {
    if (config.staticMode) {
      const { localStorageService } = await import('./localStorage')
      const saved = localStorageService.saveMap(username, mapData)
      return { data: saved }
    }
    return api.post(`/users/${username}/maps/`, mapData)
  },

  async getMap(username, mapId) {
    if (config.staticMode) {
      // Try localStorage first
      const { localStorageService } = await import('./localStorage')
      let map = localStorageService.getMap(username, mapId)
      
      if (!map) {
        // Try loading from static maps directory
        try {
          const response = await fetch(`/maps/${mapId}.json`)
          if (response.ok) {
            map = await response.json()
          }
        } catch (error) {
          console.error(`Error loading map ${mapId} from static files:`, error)
        }
      }
      
      return { data: map }
    }
    return api.get(`/users/${username}/maps/${mapId}/`)
  },

  async updateMap(username, mapId, mapData) {
    if (config.staticMode) {
      const { localStorageService } = await import('./localStorage')
      mapData.id = mapId
      const saved = localStorageService.saveMap(username, mapData)
      return { data: saved }
    }
    return api.put(`/users/${username}/maps/${mapId}/`, mapData)
  },

  async deleteMap(username, mapId) {
    if (config.staticMode) {
      const { localStorageService } = await import('./localStorage')
      const deleted = localStorageService.deleteMap(username, mapId)
      return { status: deleted ? 204 : 404 }
    }
    return api.delete(`/users/${username}/maps/${mapId}/`)
  },

  getPublicMaps() {
    return api.get('/maps/public/')
  },

  // Custom packs
  uploadCustomPack(formData) {
    return api.post('/packs/custom/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  getCustomPacks() {
    return api.get('/packs/custom/')
  },

  // ZIP packs
  uploadPackZip(formData) {
    return api.post('/packs/upload-zip/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  getUploadedPacks() {
    return api.get('/packs/uploaded/')
  },

  delete(url) {
    return api.delete(url)
  }
}
