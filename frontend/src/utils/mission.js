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
    materialRequired: '',
    tilesUsed: [],
    pageTheme: 'fantasy',
    pageEffect: 'grain',
    footerLabel: 'QUÊTE - ZOMBICIDE',
    mapImageDataUrl: null,
    cornerImage: null,
    cornerSide: 'left',
    pageBackground: null
  }
}

export function deriveTilesFromLayers (layers) {
  const tiles = layers?.tiles || []
  const codes = new Set()
  for (const t of tiles) {
    const asset = t.asset || ''
    const m = asset.match(/(\d+[RV])\.(png|webp)/i)
    if (m) codes.add(m[1].toUpperCase())
  }
  return sortTileCodes(Array.from(codes))
}

/** Pack id = premier segment du chemin asset tuile (`G-Zombicide-WD/01.tiles/...`). */
export function packIdFromTileAsset (asset) {
  if (!asset || typeof asset !== 'string') return null
  const id = asset.split(/[/\\]/)[0]?.trim()
  return id || null
}

/** Libellé boîte pour matériel requis : retire le préfixe Zombicide courant. */
export function formatMaterialPackLabel (name) {
  if (!name || typeof name !== 'string') return ''
  const trimmed = name.trim()
  const stripped = trimmed.replace(/^Zombicide\s*(Extension:\s*|:\s*)?/i, '').trim()
  return stripped || trimmed
}

/**
 * Liste unique des packs des tuiles posées → chaîne pour `mission.materialRequired`.
 * @param {object} layers
 * @param {Array<{ id: string, name?: string }>} packs
 */
export function deriveMaterialRequiredFromLayers (layers, packs = []) {
  const byId = new Map()
  for (const p of packs || []) {
    if (p?.id) byId.set(p.id, p.name || p.id)
  }
  const labels = new Set()
  for (const t of layers?.tiles || []) {
    const packId = packIdFromTileAsset(t.asset)
    if (!packId) continue
    const rawName = byId.get(packId) || packId
    const label = formatMaterialPackLabel(rawName)
    if (label) labels.add(label)
  }
  return Array.from(labels).sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' })).join(', ')
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
    materialRequired: (typeof raw.materialRequired === 'string') ? raw.materialRequired : '',
    pageEffect: (typeof raw.pageEffect === 'string') ? raw.pageEffect : 'grain',
    authors: Array.isArray(raw.authors) ? [...raw.authors] : [],
    objectives: Array.isArray(raw.objectives) ? [...raw.objectives] : [],
    specialRules: Array.isArray(raw.specialRules) ? [...raw.specialRules] : [],
    tilesUsed: Array.isArray(raw.tilesUsed) ? [...raw.tilesUsed] : [],
    mapImageDataUrl: raw.mapImageDataUrl ?? null
  }
}
