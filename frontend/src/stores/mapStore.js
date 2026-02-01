import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

export const useMapStore = defineStore('map', {
  state: () => ({
    currentPack: null,
    gridSize: { width: 10, height: 10 },
    tileSize: 10, // Grille alignée avec images 250px (250 / 10 = 25 cases)
    layers: {
      tiles: [],
      objects: []
    },
    selectedObject: null,
    history: [],
    currentMapId: null,
    mapName: 'Nouvelle carte',
    isUnsaved: true,
    gridOffsetX: 0,  // Offset global de la grille en pixels
    gridOffsetY: 0
  }),

  actions: {
    setCurrentPack(packId) {
      this.currentPack = packId
    },

    setGridSize(width, height) {
      this.gridSize = { width, height }
    },

    setTileSize(size) {
      this.tileSize = size
    },

    addTile(x, y, asset, rotation = 0) {
      // Allow overlapping tiles - don't remove existing ones
      this.layers.tiles.push({ 
        id: `tile_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        x, 
        y, 
        asset, 
        rotation 
      })
    },

    removeTile(tileId) {
      this.layers.tiles = this.layers.tiles.filter(t => t.id !== tileId)
    },

    addObject(object) {
      if (!object.id) {
        object.id = `obj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      }
      this.layers.objects.push(object)
    },

    removeObject(objectId) {
      this.layers.objects = this.layers.objects.filter(obj => obj.id !== objectId)
    },

    updateObject(objectId, updates) {
      const obj = this.layers.objects.find(o => o.id === objectId)
      if (obj) {
        Object.assign(obj, updates)
      }
    },

    selectObject(objectId) {
      this.selectedObject = objectId
    },

    clearSelection() {
      this.selectedObject = null
    },

    setGridOffset(x, y) {
      this.gridOffsetX = x
      this.gridOffsetY = y
    },

    loadMap(mapData) {
      this.currentPack = mapData.pack
      this.gridSize = mapData.grid
      this.tileSize = mapData.grid.tileSize || 32
      this.layers = mapData.layers || { tiles: [], objects: [] }
      this.currentMapId = mapData.id || null
      this.mapName = mapData.name || 'Nouvelle carte'
      this.isUnsaved = false
      this.gridOffsetX = mapData.gridOffsetX || 0
      this.gridOffsetY = mapData.gridOffsetY || 0
    },

    clearMap() {
      this.layers = { tiles: [], objects: [] }
      this.selectedObject = null
      this.currentMapId = null
      this.mapName = 'Nouvelle carte'
      this.isUnsaved = true
      this.gridOffsetX = 0
      this.gridOffsetY = 0
    }
  }
})
