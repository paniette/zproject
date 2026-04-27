/**
 * Types de jeu Zombicide (filtres Packs & Assets).
 *
 * Référence (catégories) : https://www.zombicide.com/fr/mapeditor-zombicide/
 *
 * NB: On tagge les packs côté frontend (localStorage) pour éviter de dépendre du backend.
 */

export const GAME_TYPES = [
  { id: 'all', label: 'All' },
  { id: 'classic', label: 'Classic' },
  { id: 'modern', label: 'Modern' },
  { id: 'fantasy', label: 'Fantasy' },
  { id: 'western', label: 'Western' },
  { id: 'scifi', label: 'Sci‑Fi' },
  { id: 'night', label: 'Night' }
]

/**
 * Valeurs par défaut par packId.
 * Ici, tes 4 packs actuels sont Fantasy.
 */
export const DEFAULT_PACK_GAME_TYPE = {
  'G-Zombicide-BP': 'fantasy',   // Black Plague
  'G-Zombicide-EE': 'fantasy',   // Eternal Empire
  'G-Zombicide-WD': 'fantasy',   // White Death
  'G-Zombicide-TMNT': 'fantasy', // Ninja Turtles
}

export const PACK_GAME_TYPE_STORAGE_KEY = 'zombicide_pack_game_types_v1'

export function loadPackGameTypeMap () {
  if (typeof window === 'undefined') return {}
  try {
    const raw = window.localStorage.getItem(PACK_GAME_TYPE_STORAGE_KEY)
    if (!raw) return {}
    const obj = JSON.parse(raw)
    return obj && typeof obj === 'object' ? obj : {}
  } catch (_) {
    return {}
  }
}

export function savePackGameTypeMap (map) {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem(PACK_GAME_TYPE_STORAGE_KEY, JSON.stringify(map || {}))
  } catch (_) {}
}

export function getPackGameType (packId, mapOverride) {
  const m = mapOverride || loadPackGameTypeMap()
  return m?.[packId] || DEFAULT_PACK_GAME_TYPE[packId] || 'fantasy'
}

export function getPackGameTypeFromPack (pack, mapOverride) {
  const pid = pack?.id
  const m = mapOverride || loadPackGameTypeMap()
  return m?.[pid] || pack?.gameType || DEFAULT_PACK_GAME_TYPE[pid] || 'fantasy'
}

