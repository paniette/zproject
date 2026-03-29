<template>
  <div
    class="user-selector"
    title="Les cartes sauvegardées et chargées sont celles de cet utilisateur (profil de travail)."
  >
    <label for="user-select" class="user-label">Utilisateur</label>
    <select
      id="user-select"
      v-model="selectedUser"
      class="user-select"
      aria-label="Choisir l'utilisateur actif pour les cartes"
      @change="changeUser"
    >
      <option v-for="user in availableUsers" :key="user" :value="user">
        {{ user }}
      </option>
    </select>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/userStore'
import api from '@/services/api'

const userStore = useUserStore()
const selectedUser = ref(userStore.currentUser)
const availableUsers = ref(userStore.availableUsers)

onMounted(async () => {
  try {
    const response = await api.getUsers()
    if (response.data && response.data.users) {
      availableUsers.value = response.data.users
      userStore.setAvailableUsers(response.data.users)
    }
  } catch (error) {
    console.error('Error loading users:', error)
  }
})

const changeUser = () => {
  userStore.setCurrentUser(selectedUser.value)
}
</script>

<style scoped>
.user-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  white-space: nowrap;
}

.user-select {
  padding: 6px 12px;
  min-width: 8rem;
  background: var(--brown-medium);
  color: white;
  border: 1px solid var(--brown-light);
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: border-color 0.2s, background 0.2s;
}

.user-select:hover,
.user-select:focus {
  outline: none;
  background: var(--brown-light);
  border-color: var(--primary-color);
}
</style>
