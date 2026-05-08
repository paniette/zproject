import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'zproject-editor-theme'

const VALID_THEMES = ['classic', 'modern', 'fantasy', 'western', 'scifi', 'night']

const LEGACY_MAP = {
  '':        'classic',
  'slate':   'modern',
  'necro':   'night',
  'abyss':   'scifi',
  'medieval':'fantasy',
  'eternal': 'western',
}

function normalizeLegacy (id) {
  if (VALID_THEMES.includes(id)) return id
  return LEGACY_MAP[id] ?? 'classic'
}

export const useThemeStore = defineStore('theme', () => {
  const activeTheme = ref('classic')

  function applyToDOM (id) {
    const root = document.documentElement
    if (!id || id === 'classic') {
      root.removeAttribute('data-theme')
    } else {
      root.setAttribute('data-theme', id)
    }
  }

  function setTheme (id, { syncMission = true } = {}) {
    const normalized = normalizeLegacy(id)
    activeTheme.value = normalized
    applyToDOM(normalized)
    try {
      localStorage.setItem(STORAGE_KEY, normalized)
    } catch { /* ignore */ }

    if (syncMission) {
      // Import dynamique pour éviter la dépendance circulaire au moment du chargement
      import('./mapStore').then(({ useMapStore }) => {
        const mapStore = useMapStore()
        mapStore.patchMission({ pageTheme: normalized })
      })
    }
  }

  function initTheme () {
    try {
      const saved = localStorage.getItem(STORAGE_KEY) ?? ''
      const id = normalizeLegacy(saved)
      activeTheme.value = id
      applyToDOM(id)
    } catch {
      applyToDOM('classic')
    }
  }

  return { activeTheme, setTheme, initTheme }
})
