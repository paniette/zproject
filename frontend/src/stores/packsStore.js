import { defineStore } from 'pinia'

export const usePacksStore = defineStore('packs', {
  state: () => ({
    packs: [],
    loaded: false
  }),

  actions: {
    setPacks(packs) {
      this.packs = packs
      this.loaded = true
    },

    addPack(pack) {
      this.packs.push(pack)
    },

    removePack(packId) {
      this.packs = this.packs.filter(p => p.id !== packId)
    }
  }
})
