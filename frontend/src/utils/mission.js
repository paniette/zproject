/**
 * Schéma mission et helpers (utilisé par `mapStore` et l’éditeur Mission).
 *
 * NB: ce fichier est requis par `@/utils/mission` (alias `@` -> `src`).
 */

export function defaultMission () {
  return {
    questCode: '',
    title: '',
    authors: [],
    difficulty: '',
    playerCount: '',
    estimatedDuration: '',
    synopsis: '',
    objectives: [],
    specialRules: [],
    tilesUsed: [],
    pageTheme: 'classic',
    mapImageDataUrl: null
  }
}

export function deriveTilesFromLayers (layers) {
  const tiles = layers?.tiles || []
  const codes = new Set()
  for (const t of tiles) {
    const asset = t.asset || ''
    const m = asset.match(/(\d+[RV])\.png/i)
    if (m) codes.add(m[1].toUpperCase())
  }
  return sortTileCodes(Array.from(codes))
}

function sortTileCodes (codes) {
  return codes.sort((a, b) => {
    const na = parseInt(a, 10)
    const nb = parseInt(b, 10)
    if (na !== nb) return na - nb
    return a.slice(-1).localeCompare(b.slice(-1))
  })
}

export function mergeMissionFromPayload (raw) {
  const base = defaultMission()
  if (!raw || typeof raw !== 'object') return base
  return {
    ...base,
    ...raw,
    authors: Array.isArray(raw.authors) ? [...raw.authors] : [],
    objectives: Array.isArray(raw.objectives) ? [...raw.objectives] : [],
    specialRules: Array.isArray(raw.specialRules) ? [...raw.specialRules] : [],
    tilesUsed: Array.isArray(raw.tilesUsed) ? [...raw.tilesUsed] : [],
    mapImageDataUrl: raw.mapImageDataUrl ?? null
  }
}

