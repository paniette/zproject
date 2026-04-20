/**
 * Boîte englobante (monde) d’une image posée sur la grille, avec rotation en degrés.
 * Coin haut-gauche non pivoté : (x, y), dimensions intrinsèques w×h, pivot au centre.
 */
export function boundsForImageOnGrid (x, y, imgW, imgH, rotationDeg) {
  const cx = x + imgW / 2
  const cy = y + imgH / 2
  const rad = ((rotationDeg || 0) * Math.PI) / 180
  const cos = Math.cos(rad)
  const sin = Math.sin(rad)
  const corners = [
    [-imgW / 2, -imgH / 2],
    [imgW / 2, -imgH / 2],
    [imgW / 2, imgH / 2],
    [-imgW / 2, imgH / 2]
  ]
  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity
  for (const [px, py] of corners) {
    const rx = px * cos - py * sin + cx
    const ry = px * sin + py * cos + cy
    minX = Math.min(minX, rx)
    minY = Math.min(minY, ry)
    maxX = Math.max(maxX, rx)
    maxY = Math.max(maxY, ry)
  }
  return { minX, minY, maxX, maxY }
}

export function unionBounds (boxes) {
  if (!boxes || !boxes.length) return null
  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity
  for (const b of boxes) {
    minX = Math.min(minX, b.minX)
    minY = Math.min(minY, b.minY)
    maxX = Math.max(maxX, b.maxX)
    maxY = Math.max(maxY, b.maxY)
  }
  return { minX, minY, maxX, maxY }
}

export function expandBounds (b, margin) {
  const m = margin || 0
  return {
    minX: b.minX - m,
    minY: b.minY - m,
    maxX: b.maxX + m,
    maxY: b.maxY + m
  }
}
