import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: 'temp',
    availableUsers: ['temp']
  }),

  actions: {
    setCurrentUser(username) {
      this.currentUser = username
    },

    setAvailableUsers(users) {
      this.availableUsers = users
    },

    addUser(username) {
      if (!this.availableUsers.includes(username)) {
        this.availableUsers.push(username)
      }
    }
  }
})
