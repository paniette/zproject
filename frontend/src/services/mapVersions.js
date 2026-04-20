/**
 * Historique local des versions de carte (localStorage), par id carte ou brouillon.
 */

const PREFIX = 'zproject-map-versions:'

function storageKey (mapId) {
  return PREFIX + (mapId || 'draft')
}

export function listVersions (mapId) {
  try {
    const raw = localStorage.getItem(storageKey(mapId))
    if (!raw) return []
    const arr = JSON.parse(raw)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

/** @param {object} payload — même forme que sauvegarde API (name, pack, grid, layers, …) */
export function pushVersion (mapId, label, payload) {
  try {
    const arr = listVersions(mapId)
    const entry = {
      ts: Date.now(),
      label: label || new Date().toLocaleString('fr-FR'),
      data: JSON.parse(JSON.stringify(payload))
    }
    arr.unshift(entry)
    while (arr.length > 40) arr.pop()
    localStorage.setItem(storageKey(mapId), JSON.stringify(arr))
    return entry
  } catch (e) {
    console.error('mapVersions.pushVersion', e)
    throw e
  }
}

export function clearVersions (mapId) {
  try {
    localStorage.removeItem(storageKey(mapId))
  } catch { /* ignore */ }
}
