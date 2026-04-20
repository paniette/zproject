import { defineStore } from 'pinia'
import { defaultMission, mergeMissionFromPayload } from '@/utils/mission'

const MAX_HISTORY = 50

function cloneLayers (layers) {
  return JSON.parse(JSON.stringify(layers || { tiles: [], objects: [] }))
}

function cloneMission (mission) {
  return JSON.parse(JSON.stringify(mission || defaultMission()))
}

export const useMapStore = defineStore('map', {
  state: () => ({
    currentPack: null,
    gridSize: { width: 10, height: 10 },
    tileSize: 10,
    layers: {
      tiles: [],
      objects: []
    },
    selectedObject: null,
    /** @deprecated — utiliser historyPast / historyFuture */
    history: [],
    historyPast: [],
    historyFuture: [],
    /** > 0 : mutations sans nouvel enregistrement (une seule entrée au début du compound) */
    compoundDepth: 0,
    _historySuspended: false,
    currentMapId: null,
    mapName: 'Nouvelle carte',
    isUnsaved: true,
    gridOffsetX: 0,
    gridOffsetY: 0,
    mission: defaultMission(),
    /** Lecture seule : pas de modification de la carte sur le canvas */
    isPreviewMode: false
  }),

  getters: {
    canUndo: (state) => state.historyPast.length > 0,
    canRedo: (state) => state.historyFuture.length > 0
  },

  actions: {
    clearHistoryStacks () {
      this.historyPast = []
      this.historyFuture = []
    },

    cloneMapState () {
      return {
        layers: cloneLayers(this.layers),
        gridOffsetX: this.gridOffsetX,
        gridOffsetY: this.gridOffsetY,
        gridSize: { ...this.gridSize },
        tileSize: this.tileSize,
        mission: cloneMission(this.mission)
      }
    },

    applyMapSnapshot (snap) {
      this._historySuspended = true
      try {
        this.layers = cloneLayers(snap.layers)
        this.gridOffsetX = snap.gridOffsetX
        this.gridOffsetY = snap.gridOffsetY
        this.gridSize = { ...snap.gridSize }
        this.tileSize = snap.tileSize
        this.mission = mergeMissionFromPayload(snap.mission)
      } finally {
        this._historySuspended = false
      }
    },

    _recordBeforeMutation () {
      if (this._historySuspended || this.isPreviewMode) return
      if (this.compoundDepth > 0) return
      const snap = this.cloneMapState()
      this.historyPast.push(snap)
      this.historyFuture = []
      while (this.historyPast.length > MAX_HISTORY) {
        this.historyPast.shift()
      }
    },

    beginCompound () {
      if (this._historySuspended || this.isPreviewMode) return
      if (this.compoundDepth === 0) {
        const snap = this.cloneMapState()
        this.historyPast.push(snap)
        this.historyFuture = []
        while (this.historyPast.length > MAX_HISTORY) {
          this.historyPast.shift()
        }
      }
      this.compoundDepth++
    },

    endCompound () {
      this.compoundDepth = Math.max(0, this.compoundDepth - 1)
    },

    undo () {
      if (this.historyPast.length === 0) return
      const current = this.cloneMapState()
      const prev = this.historyPast.pop()
      this.historyFuture.push(current)
      this.applyMapSnapshot(prev)
      this.isUnsaved = true
    },

    redo () {
      if (this.historyFuture.length === 0) return
      const current = this.cloneMapState()
      const next = this.historyFuture.pop()
      this.historyPast.push(current)
      this.applyMapSnapshot(next)
      this.isUnsaved = true
    },

    setPreviewMode (on) {
      this.isPreviewMode = !!on
    },

    setCurrentPack (packId) {
      this.currentPack = packId
    },

    setGridSize (width, height) {
      this._recordBeforeMutation()
      this.isUnsaved = true
      this.gridSize = { width, height }
    },

    setTileSize (size) {
      this._recordBeforeMutation()
      this.isUnsaved = true
      this.tileSize = size
    },

    addTile (x, y, asset, rotation = 0) {
      this._recordBeforeMutation()
      this.isUnsaved = true
      this.layers.tiles.push({
        id: `tile_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        x,
        y,
        asset,
        rotation
      })
    },

    removeTile (tileId) {
      this._recordBeforeMutation()
      this.isUnsaved = true
      this.layers.tiles = this.layers.tiles.filter(t => t.id !== tileId)
    },

    updateTile (tileId, updates) {
      this._recordBeforeMutation()
      this.isUnsaved = true
      const i = this.layers.tiles.findIndex(t => t.id === tileId)
      if (i === -1) return
      const tile = this.layers.tiles[i]
      this.layers.tiles.splice(i, 1, { ...tile, ...updates })
    },

    addObject (object) {
      this._recordBeforeMutation()
      this.isUnsaved = true
      if (!object.id) {
        object.id = `obj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      }
      this.layers.objects.push(object)
    },

    removeObject (objectId) {
      this._recordBeforeMutation()
      this.isUnsaved = true
      this.layers.objects = this.layers.objects.filter(obj => obj.id !== objectId)
    },

    updateObject (objectId, updates) {
      this._recordBeforeMutation()
      this.isUnsaved = true
      const obj = this.layers.objects.find(o => o.id === objectId)
      if (obj) {
        Object.assign(obj, updates)
      }
    },

    selectObject (objectId) {
      this.selectedObject = objectId
    },

    clearSelection () {
      this.selectedObject = null
    },

    setGridOffset (x, y) {
      // Pan : pas d'historique
      this.gridOffsetX = x
      this.gridOffsetY = y
    },

    loadMap (mapData) {
      this.clearHistoryStacks()
      this.compoundDepth = 0
      this.isPreviewMode = false
      this.currentPack = mapData.pack
      this.gridSize = mapData.grid
      this.tileSize = mapData.grid.tileSize || 32
      this.layers = mapData.layers || { tiles: [], objects: [] }
      this.currentMapId = mapData.id || null
      this.mapName = mapData.name || 'Nouvelle carte'
      this.isUnsaved = false
      this.gridOffsetX = mapData.gridOffsetX || 0
      this.gridOffsetY = mapData.gridOffsetY || 0
      this.mission = mergeMissionFromPayload(mapData.mission)
    },

    setMission (updates) {
      this._recordBeforeMutation()
      this.isUnsaved = true
      this.mission = mergeMissionFromPayload({ ...this.mission, ...updates })
    },

    patchMission (partial) {
      this._recordBeforeMutation()
      this.isUnsaved = true
      this.mission = mergeMissionFromPayload({ ...this.mission, ...partial })
    },

    clearMap () {
      this.clearHistoryStacks()
      this.compoundDepth = 0
      this.isPreviewMode = false
      this.layers = { tiles: [], objects: [] }
      this.selectedObject = null
      this.currentMapId = null
      this.mapName = 'Nouvelle carte'
      this.isUnsaved = true
      this.gridOffsetX = 0
      this.gridOffsetY = 0
      this.mission = defaultMission()
    }
  }
})
