<template>
  <div class="theme-selector">
    <label for="theme-select" class="theme-label">Thème</label>
    <select
      id="theme-select"
      :value="themeStore.activeTheme"
      class="theme-select"
      aria-label="Choisir le thème de l'interface"
      @change="themeStore.setTheme($event.target.value)"
    >
      <option v-for="opt in GAME_TYPES.filter(t => t.id !== 'all')" :key="opt.id" :value="opt.id">
        {{ opt.label }}
      </option>
    </select>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/themeStore'
import { GAME_TYPES } from '@/config/gameTypes'

const themeStore = useThemeStore()
</script>

<style scoped>
.theme-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.theme-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  white-space: nowrap;
}

.theme-select {
  padding: 6px 10px;
  min-width: 11rem;
  background: var(--brown-medium);
  color: white;
  border: 1px solid var(--brown-light);
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: border-color 0.2s, background 0.2s;
}

.theme-select:hover,
.theme-select:focus {
  outline: none;
  background: var(--brown-light);
  border-color: var(--primary-color);
}
</style>
