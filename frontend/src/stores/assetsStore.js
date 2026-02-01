import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAssetsStore = defineStore('assets', {
  state: () => ({
    packs: [],
    currentPack: null,
    assets: {}
  }),

  actions: {
    setPacks(packs) {
      this.packs = packs
    },

    setCurrentPack(packId) {
      this.currentPack = packId
    },

    setAssets(packId, assets) {
      this.assets[packId] = assets
    },

    getAssetsByCategory(packId, category) {
      if (!this.assets[packId]) return []
      return this.assets[packId][category] || []
    }
  }
})
