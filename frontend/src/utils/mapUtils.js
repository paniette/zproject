/**
 * Utility functions for map operations
 */

export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

export function snapToGrid(value, gridSize) {
  return Math.floor(value / gridSize) * gridSize
}

export function isValidGridPosition(x, y, width, height) {
  return x >= 0 && x < width && y >= 0 && y < height
}

export function generateMapId() {
  return `map_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

export function formatDate(date) {
  return new Date(date).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * URL de vignette pour MapLoader (API, localStorage, ou index statique + maps/thumbs/).
 * @param {{ id?: string, thumbUrl?: string, mission?: { mapImageDataUrl?: string } }} map
 * @returns {string|null}
 */
export function mapThumbSrc (map) {
  if (!map) return null
  const dataUrl = map.mission?.mapImageDataUrl
  if (dataUrl) return dataUrl

  const base = import.meta.env.BASE_URL || ''
  const resolve = (path) => {
    if (!path) return null
    if (/^https?:\/\//i.test(path) || path.startsWith('data:')) return path
    const rel = path.startsWith('/') ? path.slice(1) : path
    return `${base}${rel}`
  }

  if (map.thumbUrl) return resolve(map.thumbUrl)
  if (map.id) return resolve(`maps/thumbs/${map.id}.png`)
  return null
}
