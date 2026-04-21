/**
 * Local storage service for static mode
 * Saves maps to browser localStorage/IndexedDB
 */

const STORAGE_KEY_PREFIX = 'zombicide_maps_'
const MAPS_LIST_KEY = 'zombicide_maps_list'
/** Cartes servies uniquement par fichiers statiques : masquées localement après « Supprimer » */
const SUPPRESSED_STATIC_MAPS_KEY = 'zombicide_static_maps_suppressed'

function readSuppressedByUser () {
  try {
    return JSON.parse(localStorage.getItem(SUPPRESSED_STATIC_MAPS_KEY) || '{}')
  } catch {
    return {}
  }
}

function writeSuppressedByUser (obj) {
  localStorage.setItem(SUPPRESSED_STATIC_MAPS_KEY, JSON.stringify(obj))
}

export const localStorageService = {
  /**
   * IDs des cartes « statiques » (JSON sur le serveur) masquées pour cet utilisateur dans le modal Charger.
   */
  getSuppressedStaticMapIds (username) {
    const byUser = readSuppressedByUser()
    const ids = byUser[username]
    return Array.isArray(ids) ? new Set(ids) : new Set()
  },

  /**
   * Masque une carte qui n’existe que dans l’index /maps/*.json (impossible d’effacer le fichier sur le FTP).
   */
  suppressStaticMapListing (username, mapId) {
    const byUser = readSuppressedByUser()
    if (!byUser[username]) byUser[username] = []
    if (!byUser[username].includes(mapId)) byUser[username].push(mapId)
    writeSuppressedByUser(byUser)
  },

  /**
   * Get all maps for a user
   */
  getUserMaps(username) {
    try {
      const mapsList = JSON.parse(localStorage.getItem(MAPS_LIST_KEY) || '[]')
      return mapsList.filter(map => map.metadata?.author === username)
    } catch (error) {
      console.error('Error loading maps from localStorage:', error)
      return []
    }
  },

  /**
   * Get a specific map
   */
  getMap(username, mapId) {
    try {
      const key = `${STORAGE_KEY_PREFIX}${mapId}`
      const mapData = JSON.parse(localStorage.getItem(key) || 'null')
      
      if (mapData && mapData.metadata?.author === username) {
        return mapData
      }
      return null
    } catch (error) {
      console.error('Error loading map from localStorage:', error)
      return null
    }
  },

  /**
   * Save a map
   */
  saveMap(username, mapData) {
    try {
      const mapId = mapData.id || `map_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      mapData.id = mapId
      
      // Ensure metadata
      if (!mapData.metadata) {
        mapData.metadata = {}
      }
      mapData.metadata.author = username
      mapData.metadata.modified = new Date().toISOString()
      if (!mapData.metadata.created) {
        mapData.metadata.created = mapData.metadata.modified
      }
      
      // Save map
      const key = `${STORAGE_KEY_PREFIX}${mapId}`
      localStorage.setItem(key, JSON.stringify(mapData))
      
      // Update maps list
      const mapsList = JSON.parse(localStorage.getItem(MAPS_LIST_KEY) || '[]')
      const existingIndex = mapsList.findIndex(m => m.id === mapId)
      
      const listEntry = {
        id: mapId,
        name: mapData.name,
        metadata: mapData.metadata
      }
      
      if (existingIndex >= 0) {
        mapsList[existingIndex] = listEntry
      } else {
        mapsList.push(listEntry)
      }
      
      // Sort by modified date (most recent first)
      mapsList.sort((a, b) => {
        const dateA = a.metadata?.modified || ''
        const dateB = b.metadata?.modified || ''
        return dateB.localeCompare(dateA)
      })
      
      localStorage.setItem(MAPS_LIST_KEY, JSON.stringify(mapsList))
      
      return mapData
    } catch (error) {
      console.error('Error saving map to localStorage:', error)
      throw error
    }
  },

  /**
   * Delete a map
   */
  deleteMap(username, mapId) {
    try {
      const key = `${STORAGE_KEY_PREFIX}${mapId}`
      const mapData = this.getMap(username, mapId)
      
      if (!mapData) {
        return false
      }
      
      // Remove from storage
      localStorage.removeItem(key)
      
      // Remove from list
      const mapsList = JSON.parse(localStorage.getItem(MAPS_LIST_KEY) || '[]')
      const filtered = mapsList.filter(m => m.id !== mapId)
      localStorage.setItem(MAPS_LIST_KEY, JSON.stringify(filtered))
      
      return true
    } catch (error) {
      console.error('Error deleting map from localStorage:', error)
      return false
    }
  }
}
