/**
 * Tuiles Zombicide : un même numéro existe en recto (R) et verso (V).
 * Une seule face de la paire peut être sur la carte à la fois.
 */

const TILES_SEGMENT = '/01.tiles/'

/**
 * Exemple : G-Zombicide-BP/01.tiles/39R.png/r_0.png (ou .webp) → clé "G-Zombicide-BP|39"
 * @param {string} assetPath
 * @returns {string|null}
 */
export function zombicideTilePairKey (assetPath) {
  if (!assetPath || typeof assetPath !== 'string') return null
  const normalized = assetPath.replace(/\\/g, '/')
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

const TILE_CATEGORIES = new Set(['tiles', '01.tiles'])

/**
 * @param {string} assetPath
 * @param {string} category
 * @param {Set<string>} usedKeys
 */
export function isTilePairLocked (assetPath, category, usedKeys) {
  if (!usedKeys || !usedKeys.size) return false
  if (!TILE_CATEGORIES.has(category)) return false
  const k = zombicideTilePairKey(assetPath)
  if (!k) return false
  return usedKeys.has(k)
}
