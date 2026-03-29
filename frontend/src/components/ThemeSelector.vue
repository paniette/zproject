<template>
  <div class="theme-selector">
    <label for="theme-select" class="theme-label">Thème</label>
    <select
      id="theme-select"
      v-model="themeId"
      class="theme-select"
      aria-label="Choisir le thème de l’interface"
    >
      <option v-for="opt in themes" :key="opt.id" :value="opt.id">
        {{ opt.label }}
      </option>
    </select>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const STORAGE_KEY = 'zproject-editor-theme'

const themes = [
  { id: '', label: 'Classique (survivants)' },
  { id: 'slate', label: 'Ardoise' },
  { id: 'necro', label: 'Nécrose' },
  { id: 'abyss', label: 'Abyssal' }
]

const themeId = ref('')

function applyTheme (id) {
  const root = document.documentElement
  if (!id) {
    root.removeAttribute('data-theme')
  } else {
    root.setAttribute('data-theme', id)
  }
  try {
    localStorage.setItem(STORAGE_KEY, id || '')
  } catch {
    /* ignore */
  }
}

onMounted(() => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved !== null && saved !== '') {
      themeId.value = saved
    }
  } catch {
    /* ignore */
  }
  applyTheme(themeId.value)
})

watch(themeId, (id) => applyTheme(id))
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
