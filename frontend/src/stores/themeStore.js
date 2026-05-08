import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'zproject-editor-theme'
const STORAGE_KEY_ASSET_FILTER = 'zproject-asset-game-type-filter'

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
  // Filtre assets/packs: 'all' ou un gameType (classic/modern/...)
  const assetGameTypeFilter = ref('all')

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

    // Si l’utilisateur choisit explicitement un thème, on garde aussi le filtre assets aligné
    // (sauf action volontaire sur "all" gérée côté AssetPanel).
    assetGameTypeFilter.value = normalized
    try {
      localStorage.setItem(STORAGE_KEY_ASSET_FILTER, normalized)
    } catch { /* ignore */ }

    if (syncMission) {
      // Import dynamique pour éviter la dépendance circulaire au moment du chargement
      import('./mapStore').then(({ useMapStore }) => {
        const mapStore = useMapStore()
        mapStore.patchMission({ pageTheme: normalized })
      })
    }
  }

  function setAssetGameTypeFilter (id) {
    if (id === 'all') {
      assetGameTypeFilter.value = 'all'
    } else {
      assetGameTypeFilter.value = normalizeLegacy(id)
    }
    try {
      localStorage.setItem(STORAGE_KEY_ASSET_FILTER, assetGameTypeFilter.value)
    } catch { /* ignore */ }
  }

  function initTheme () {
    try {
      const saved = localStorage.getItem(STORAGE_KEY) ?? ''
      const id = normalizeLegacy(saved)
      activeTheme.value = id
      applyToDOM(id)

      const savedFilter = localStorage.getItem(STORAGE_KEY_ASSET_FILTER) ?? 'all'
      assetGameTypeFilter.value = savedFilter === 'all' ? 'all' : normalizeLegacy(savedFilter)
    } catch {
      applyToDOM('classic')
    }
  }

  return { activeTheme, assetGameTypeFilter, setTheme, setAssetGameTypeFilter, initTheme }
})
