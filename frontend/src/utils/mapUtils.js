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
