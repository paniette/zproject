import { defineStore } from 'pinia'

export const useToolStore = defineStore('tool', {
  state: () => ({
    activeTool: 'move', // 'place', 'move', 'rotate', 'delete' - 'move' par défaut
    selectedObject: null // ID of selected object/tile
  }),

  actions: {
    setTool(tool) {
      this.activeTool = tool
      this.selectedObject = null
    },

    selectObject(objectId) {
      this.selectedObject = objectId
    },

    clearSelection() {
      this.selectedObject = null
    }
  }
})
