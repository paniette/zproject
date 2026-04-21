/**
 * Tuiles Zombicide : un même numéro existe en recto (R) et verso (V).
 * Une seule face de la paire peut être sur la carte à la fois.
 */

const TILES_SEGMENT = '/01.tiles/'
const TILE_CATEGORIES = new Set(['tiles', '01.tiles'])

function normalizePathForTilePair (assetPath) {
  if (!assetPath || typeof assetPath !== 'string') return ''
  let p = assetPath.replace(/\\/g, '/')
  while (p.startsWith('./')) p = p.slice(2)
  if (p.startsWith('assets/')) p = p.slice('assets/'.length)
  if (p.startsWith('bgmapeditor_tiles/')) p = p.slice('bgmapeditor_tiles/'.length)
  return p
}

/**
 * Ex. `G-Zombicide-BP/01.tiles/39R.png` → `G-Zombicide-BP|39`
 * @param {string} assetPath
 * @returns {string|null}
 */
export function zombicideTilePairKey (assetPath) {
  if (!assetPath || typeof assetPath !== 'string') return null
  const normalized = normalizePathForTilePair(assetPath)
  if (!normalized.includes(TILES_SEGMENT)) return null
  const m = normalized.match(/(\d+)[RV]\.(png|webp)/i)
  if (!m) return null
  const num = m[1]
  const idx = normalized.indexOf(TILES_SEGMENT)
  const packPrefix = idx >= 0 ? normalized.slice(0, idx) : ''
  return `${packPrefix}|${num}`
}

/**
 * @param {Array<{ asset: string }>} tiles
 * @returns {Set<string>}
 */
export function collectUsedTilePairKeys (tiles) {
  const set = new Set()
  for (const t of tiles || []) {
    const k = zombicideTilePairKey(t.asset)
    if (k) set.add(k)
  }
  return set
}

/**
 * @param {string} assetPath
 * @param {string} category — toujours présent (injecté par api.js en statique comme en Django)
 * @param {Set<string>} usedKeys
 */
export function isTilePairLocked (assetPath, category, usedKeys) {
  if (!usedKeys || !usedKeys.size) return false
  if (!TILE_CATEGORIES.has(category)) return false
  const k = zombicideTilePairKey(assetPath)
  if (!k) return false
  return usedKeys.has(k)
}
