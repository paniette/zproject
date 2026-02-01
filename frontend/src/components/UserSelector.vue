<template>
  <div class="user-selector">
    <select v-model="selectedUser" @change="changeUser" class="user-select">
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
}

.user-select {
  padding: 6px 12px;
  background: var(--brown-medium);
  color: white;
  border: 1px solid var(--brown-light);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.user-select:hover {
  background: var(--brown-light);
  border-color: var(--primary-color);
}
</style>
