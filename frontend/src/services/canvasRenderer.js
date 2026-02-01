/**
 * Canvas rendering utilities for the map editor
 */

export function renderTile(ctx, image, x, y, tileSize, rotation = 0) {
  if (!image) return

  ctx.save()
  ctx.translate(x * tileSize + tileSize / 2, y * tileSize + tileSize / 2)
  ctx.rotate((rotation * Math.PI) / 180)
  ctx.drawImage(image, -tileSize / 2, -tileSize / 2, tileSize, tileSize)
  ctx.restore()
}

export function renderObject(ctx, image, x, y, tileSize, rotation = 0) {
  if (!image) return

  ctx.save()
  ctx.translate(x * tileSize + tileSize / 2, y * tileSize + tileSize / 2)
  ctx.rotate((rotation * Math.PI) / 180)
  ctx.drawImage(image, -tileSize / 2, -tileSize / 2, tileSize, tileSize)
  ctx.restore()
}

export function renderGrid(ctx, width, height, tileSize, offsetX = 0, offsetY = 0, canvasWidth = null, canvasHeight = null, gridOffsetX = 0, gridOffsetY = 0) {
  // Use visible grid lines (dark gray/black with opacity)
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)'
  ctx.lineWidth = 1 // Constant 1px thickness

  // Get canvas dimensions if provided, otherwise use grid dimensions
  const maxWidth = canvasWidth || (width * tileSize)
  const maxHeight = canvasHeight || (height * tileSize)

  // Apply grid offset to the grid rendering
  const gridStartX = offsetX + gridOffsetX
  const gridStartY = offsetY + gridOffsetY

  // Draw vertical lines across entire visible area
  const startX = Math.floor(gridStartX / tileSize) * tileSize
  const endX = Math.ceil((gridStartX + maxWidth) / tileSize) * tileSize
  
  for (let x = startX; x <= endX; x += tileSize) {
    ctx.beginPath()
    ctx.moveTo(x, gridStartY)
    ctx.lineTo(x, gridStartY + maxHeight)
    ctx.stroke()
  }

  // Draw horizontal lines across entire visible area
  const startY = Math.floor(gridStartY / tileSize) * tileSize
  const endY = Math.ceil((gridStartY + maxHeight) / tileSize) * tileSize
  
  for (let y = startY; y <= endY; y += tileSize) {
    ctx.beginPath()
    ctx.moveTo(gridStartX, y)
    ctx.lineTo(gridStartX + maxWidth, y)
    ctx.stroke()
  }
}

export function getGridCoordinates(clientX, clientY, canvas, tileSize, zoom = 1, panX = 0, panY = 0, gridOffsetX = 0, gridOffsetY = 0) {
  const rect = canvas.getBoundingClientRect()
  // Convert screen coordinates to world coordinates
  // Account for pan, zoom, and grid offset transformation
  const worldX = (clientX - rect.left - panX) / zoom - gridOffsetX
  const worldY = (clientY - rect.top - panY) / zoom - gridOffsetY
  // Convert to grid coordinates
  const x = Math.floor(worldX / tileSize)
  const y = Math.floor(worldY / tileSize)
  return { x, y }
}

export function getGridCoordinatesWithSnap(clientX, clientY, canvas, tileSize, zoom = 1, panX = 0, panY = 0, gridOffsetX = 0, gridOffsetY = 0) {
  const rect = canvas.getBoundingClientRect()
  // Convert screen coordinates to world coordinates
  // Account for pan, zoom, and grid offset transformation
  const worldX = (clientX - rect.left - panX) / zoom - gridOffsetX
  const worldY = (clientY - rect.top - panY) / zoom - gridOffsetY
  // Snap to grid
  const snappedX = Math.round(worldX / tileSize) * tileSize
  const snappedY = Math.round(worldY / tileSize) * tileSize
  // Convert to grid coordinates
  const x = Math.round(worldX / tileSize)
  const y = Math.round(worldY / tileSize)
  return { x, y, worldX: snappedX, worldY: snappedY }
}
