<template>
  <div class="canvas-grid">
    <Toolbar />
    <canvas
      ref="canvasRef"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @wheel="handleWheel"
      :class="{ 'grab-cursor': isPanning || (!hoveredItem && !isDragging), 'grabbing-cursor': isDragging && isPanning }"
    ></canvas>
    <div class="canvas-controls">
      <button @click="zoomIn">+</button>
      <button @click="zoomOut">-</button>
      <button @click="resetZoom">Reset</button>
      <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useToolStore } from '@/stores/toolStore'
import { renderGrid, getGridCoordinates, getGridCoordinatesWithSnap } from '@/services/canvasRenderer'
import Toolbar from './Toolbar.vue'

const mapStore = useMapStore()
const toolStore = useToolStore()
const canvasRef = ref(null)
const ctx = ref(null)

const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
const isDragging = ref(false)
const isPanning = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const selectedAsset = ref(null)
const draggedObject = ref(null)
const dragStartCoords = ref({ x: 0, y: 0 })
const dragOffset = ref({ x: 0, y: 0 }) // Offset du curseur par rapport à l'image au début du drag
const hoveredItem = ref(null)

const imageCache = new Map() // Store: { image: Image, width: number, height: number }
const isDrawing = ref(false) // Flag to prevent concurrent draws
const gridInitialized = ref(false) // Flag pour savoir si la grille a été initialisée


onMounted(() => {
  const canvas = canvasRef.value
  if (canvas) {
    ctx.value = canvas.getContext('2d')
    resizeCanvas()
    draw()
  }

  window.addEventListener('resize', resizeCanvas)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCanvas)
})

watch(() => mapStore.layers, () => {
  draw()
}, { deep: true })

watch(() => toolStore.selectedObject, () => {
  draw()
})

// Réinitialiser le flag d'initialisation de la grille quand on charge une carte
watch(() => mapStore.currentMapId, (newId, oldId) => {
  if (newId !== oldId) {
    // Si on charge une carte qui n'a pas de gridOffset sauvegardé, réinitialiser le flag
    if (mapStore.gridOffsetX === 0 && mapStore.gridOffsetY === 0) {
      gridInitialized.value = false
      // Réinitialiser la grille après un court délai pour que le canvas soit prêt
      setTimeout(() => {
        resizeCanvas()
      }, 100)
    }
  }
})

// Note: draw() is called manually in handleMouseMove when hoveredItem changes
// to avoid double rendering. The watcher is kept for other cases.
watch(() => hoveredItem.value, () => {
  // Only draw if not already drawing (avoid double render on hover)
  // draw() is already called in handleMouseMove when hover changes
})

const resizeCanvas = () => {
  const canvas = canvasRef.value
  if (canvas) {
    const container = canvas.parentElement
    canvas.width = container.clientWidth
    canvas.height = container.clientHeight
    
    // Initialiser la position de la grille pour qu'elle soit centrée (une seule fois au premier chargement)
    // La grille fait 4x la taille du canvas, donc on la décale de -1.5x pour la centrer
    if (!gridInitialized.value && mapStore.gridOffsetX === 0 && mapStore.gridOffsetY === 0) {
      const gridWidth = (canvas.width / zoom.value) * 4
      const gridHeight = (canvas.height / zoom.value) * 4
      // Centrer la grille : décaler de -1.5x la taille du canvas visible
      mapStore.setGridOffset(
        -(gridWidth - canvas.width / zoom.value) / 2,
        -(gridHeight - canvas.height / zoom.value) / 2
      )
      gridInitialized.value = true
    }
    
    draw()
  }
}

const draw = async () => {
  if (!ctx.value || !canvasRef.value) return
  
  // Prevent concurrent draws
  if (isDrawing.value) return
  isDrawing.value = true

  try {
    const canvas = canvasRef.value
    
    // Fill canvas with white background
    ctx.value.fillStyle = '#ffffff'
    ctx.value.fillRect(0, 0, canvas.width, canvas.height)

    // Apply pan and zoom
    ctx.value.save()
    ctx.value.translate(panX.value, panY.value)
    ctx.value.scale(zoom.value, zoom.value)

  // Draw grid covering entire canvas and extending 4x for large maps (in world space, so squares scale with zoom)
  const gridWidth = (canvas.width / zoom.value) * 4
  const gridHeight = (canvas.height / zoom.value) * 4
  renderGrid(
    ctx.value,
    mapStore.gridSize.width,
    mapStore.gridSize.height,
    mapStore.tileSize,
    0,
    0,
    gridWidth,
    gridHeight,
    mapStore.gridOffsetX,
    mapStore.gridOffsetY
  )

  // Draw tiles - wait for all to complete
  await Promise.all(
    mapStore.layers.tiles.map(tile => drawTile(tile))
  )

  // Draw objects - wait for all to complete
  await Promise.all(
    mapStore.layers.objects.map(obj => drawObject(obj))
  )

  // Draw hover highlight (before selection)
  if (hoveredItem.value && hoveredItem.value !== toolStore.selectedObject) {
    drawHover()
  }

  // Draw selection highlight
  if (toolStore.selectedObject) {
    drawSelection()
  }

  ctx.value.restore()
  } finally {
    isDrawing.value = false
  }
}

const loadImage = (assetPath) => {
  return new Promise((resolve) => {
    if (imageCache.has(assetPath)) {
      resolve(imageCache.get(assetPath))
      return
    }

    const img = new Image()
    img.onload = () => {
      // Store image with its dimensions
      const imageData = {
        image: img,
        width: img.width,
        height: img.height
      }
      imageCache.set(assetPath, imageData)
      resolve(imageData)
    }
    img.onerror = () => resolve(null)
    // Try both /assets/ and /bgmapeditor_tiles/ paths
    if (assetPath.startsWith('assets/') || assetPath.startsWith('bgmapeditor_tiles/')) {
      img.src = `/${assetPath}`
    } else {
      img.src = `/assets/${assetPath}`
    }
  })
}

const drawTile = async (tile) => {
  if (!ctx.value) return

  const imageData = await loadImage(tile.asset)
  if (imageData && imageData.image) {
    ctx.value.save()
    // Use real image dimensions
    const img = imageData.image
    const imgWidth = imageData.width
    const imgHeight = imageData.height
    
    // Positionner l'image pour que son coin supérieur gauche soit aligné avec la grille
    // Le coin supérieur gauche de l'image est à (tile.x * tileSize + gridOffsetX, tile.y * tileSize + gridOffsetY)
    const x = tile.x * mapStore.tileSize + mapStore.gridOffsetX
    const y = tile.y * mapStore.tileSize + mapStore.gridOffsetY
    
    // Pour la rotation, on centre sur le centre de l'image
    ctx.value.translate(x + imgWidth / 2, y + imgHeight / 2)
    ctx.value.rotate((tile.rotation * Math.PI) / 180)
    ctx.value.drawImage(
      img,
      -imgWidth / 2,
      -imgHeight / 2,
      imgWidth,
      imgHeight
    )
    ctx.value.restore()
  }
}

const drawObject = async (obj) => {
  if (!ctx.value) return

  const imageData = await loadImage(obj.asset)
  if (imageData && imageData.image) {
    ctx.value.save()
    // Use real image dimensions
    const img = imageData.image
    const imgWidth = imageData.width
    const imgHeight = imageData.height
    
    // Positionner l'image pour que son coin supérieur gauche soit aligné avec la grille
    // Le coin supérieur gauche de l'image est à (obj.x * tileSize + gridOffsetX, obj.y * tileSize + gridOffsetY)
    const x = obj.x * mapStore.tileSize + mapStore.gridOffsetX
    const y = obj.y * mapStore.tileSize + mapStore.gridOffsetY
    
    // Pour la rotation, on centre sur le centre de l'image
    ctx.value.translate(x + imgWidth / 2, y + imgHeight / 2)
    ctx.value.rotate((obj.rotation * Math.PI) / 180)
    ctx.value.drawImage(
      img,
      -imgWidth / 2,
      -imgHeight / 2,
      imgWidth,
      imgHeight
    )
    ctx.value.restore()
  }
}

const drawHover = () => {
  if (!ctx.value || !hoveredItem.value) return
  
  const obj = mapStore.layers.objects.find(o => o.id === hoveredItem.value)
  const tile = obj ? null : mapStore.layers.tiles.find(t => t.id === hoveredItem.value)
  const item = obj || tile
  
  if (!item) return
  
  const imageData = imageCache.get(item.asset)
  if (!imageData) return
  
  // Ne pas faire save/restore ici car on est déjà dans le contexte transformé
  // Le contexte principal a déjà le zoom appliqué via ctx.scale()
  // On doit juste sauvegarder l'état actuel pour les transformations de position/rotation
  ctx.value.save()
  
  // Dessiner le halo exactement comme l'image (même transformation)
  const imgWidth = imageData.width
  const imgHeight = imageData.height
  
  // Même transformation que pour l'image (coin supérieur gauche aligné avec grille)
  const x = item.x * mapStore.tileSize + mapStore.gridOffsetX
  const y = item.y * mapStore.tileSize + mapStore.gridOffsetY
  
  // Pour la rotation, on centre sur le centre de l'image
  ctx.value.translate(x + imgWidth / 2, y + imgHeight / 2)
  ctx.value.rotate((item.rotation * Math.PI) / 180)
  
  // Halo bleu clair pour survol - dessiner autour de l'image
  // Le lineWidth doit être inversement proportionnel au zoom pour rester constant en pixels d'écran
  // Le contexte a déjà ctx.scale(zoom.value, zoom.value) appliqué, donc on divise par zoom
  const currentZoom = zoom.value
  ctx.value.fillStyle = 'rgba(100, 150, 255, 0.2)'
  ctx.value.strokeStyle = 'rgba(100, 150, 255, 0.6)'
  ctx.value.lineWidth = 2 / currentZoom
  
  // Dessiner le rectangle autour de l'image (centré comme l'image)
  ctx.value.fillRect(-imgWidth / 2, -imgHeight / 2, imgWidth, imgHeight)
  ctx.value.strokeRect(-imgWidth / 2, -imgHeight / 2, imgWidth, imgHeight)
  ctx.value.restore()
}

const drawSelection = () => {
  if (!ctx.value || !toolStore.selectedObject) return
  
  // Find selected object or tile
  const obj = mapStore.layers.objects.find(o => o.id === toolStore.selectedObject)
  const tile = obj ? null : mapStore.layers.tiles.find(t => t.id === toolStore.selectedObject)
  const item = obj || tile
  
  if (!item) return
  
  // Get image dimensions for selection box
  const imageData = imageCache.get(item.asset)
  if (!imageData) return
  
  // Ne pas faire save/restore ici car on est déjà dans le contexte transformé
  // Le contexte principal a déjà le zoom appliqué via ctx.scale()
  // On doit juste sauvegarder l'état actuel pour les transformations de position/rotation
  ctx.value.save()
  
  // Dessiner le halo exactement comme l'image (même transformation)
  const imgWidth = imageData.width
  const imgHeight = imageData.height
  
  // Même transformation que pour l'image (coin supérieur gauche aligné avec grille)
  const x = item.x * mapStore.tileSize + mapStore.gridOffsetX
  const y = item.y * mapStore.tileSize + mapStore.gridOffsetY
  
  // Pour la rotation, on centre sur le centre de l'image
  ctx.value.translate(x + imgWidth / 2, y + imgHeight / 2)
  ctx.value.rotate((item.rotation * Math.PI) / 180)
  
  // Halo vert pour sélection - dessiner autour de l'image
  // Le lineWidth doit être inversement proportionnel au zoom pour rester constant en pixels d'écran
  // Le contexte a déjà ctx.scale(zoom.value, zoom.value) appliqué, donc on divise par zoom
  const currentZoom = zoom.value
  ctx.value.fillStyle = 'rgba(76, 175, 80, 0.1)' // Fond vert très clair (réduit)
  ctx.value.strokeStyle = 'rgba(76, 175, 80, 0.5)' // Contour vert (réduit)
  ctx.value.lineWidth = 2 / currentZoom // Ligne constante en pixels d'écran
  
  // Dessiner le rectangle autour de l'image (centré comme l'image)
  ctx.value.fillRect(-imgWidth / 2, -imgHeight / 2, imgWidth, imgHeight)
  ctx.value.strokeRect(-imgWidth / 2, -imgHeight / 2, imgWidth, imgHeight)
  ctx.value.restore()
}

// Helper to find object/tile at grid coordinates (for placement)
const findItemAtCoords = (coords) => {
  // Check objects first (they're on top)
  const obj = mapStore.layers.objects.find(
    o => o.x === coords.x && o.y === coords.y
  )
  if (obj) return { type: 'object', item: obj }
  
  // Then check tiles
  const tile = mapStore.layers.tiles.find(
    t => t.x === coords.x && t.y === coords.y
  )
  if (tile) return { type: 'tile', item: tile }
  
  return null
}

// Helper to find object/tile at world pixel coordinates (for hover detection)
const findItemAtWorldCoords = (worldX, worldY) => {
  // Check all objects and tiles to see if the point is within their bounds
  // Check objects first (they're on top)
  for (const obj of mapStore.layers.objects) {
    const imageData = imageCache.get(obj.asset)
    if (!imageData) continue
    
    const imgWidth = imageData.width
    const imgHeight = imageData.height
    // Coin supérieur gauche de l'image (aligné avec grille)
    const x = obj.x * mapStore.tileSize + mapStore.gridOffsetX
    const y = obj.y * mapStore.tileSize + mapStore.gridOffsetY
    
    // Check if point is within image bounds (simplified - doesn't account for rotation yet)
    if (worldX >= x && worldX <= x + imgWidth && worldY >= y && worldY <= y + imgHeight) {
      return { type: 'object', item: obj }
    }
  }
  
  // Then check tiles
  for (const tile of mapStore.layers.tiles) {
    const imageData = imageCache.get(tile.asset)
    if (!imageData) continue
    
    const imgWidth = imageData.width
    const imgHeight = imageData.height
    // Coin supérieur gauche de l'image (aligné avec grille)
    const x = tile.x * mapStore.tileSize + mapStore.gridOffsetX
    const y = tile.y * mapStore.tileSize + mapStore.gridOffsetY
    
    // Check if point is within image bounds (simplified - doesn't account for rotation yet)
    if (worldX >= x && worldX <= x + imgWidth && worldY >= y && worldY <= y + imgHeight) {
      return { type: 'tile', item: tile }
    }
  }
  
  return null
}

const handleMouseDown = (event) => {
  if (event.button === 0) { // Left click
    // Convertir en coordonnées monde pour détecter si on clique sur un élément (comme pour hover)
    const rect = canvasRef.value.getBoundingClientRect()
    const worldX = (event.clientX - rect.left - panX.value) / zoom.value
    const worldY = (event.clientY - rect.top - panY.value) / zoom.value
    
    // Chercher un élément aux coordonnées monde (détecte toute la surface de l'image)
    let found = findItemAtWorldCoords(worldX, worldY)
    
    // Si pas trouvé avec worldCoords, essayer avec hoveredItem
    if (!found && hoveredItem.value) {
      const obj = mapStore.layers.objects.find(o => o.id === hoveredItem.value)
      const tile = obj ? null : mapStore.layers.tiles.find(t => t.id === hoveredItem.value)
      if (obj || tile) {
        found = { type: obj ? 'object' : 'tile', item: obj || tile }
      }
    }
    
    // Si toujours pas trouvé, utiliser les coordonnées de grille (pour placement)
    const coords = getGridCoordinatesWithSnap(
      event.clientX,
      event.clientY,
      canvasRef.value,
      mapStore.tileSize,
      zoom.value,
      panX.value,
      panY.value,
      mapStore.gridOffsetX,
      mapStore.gridOffsetY
    )
    if (!found) {
      found = findItemAtCoords(coords)
    }
    
    // Handle different tools
    if (toolStore.activeTool === 'delete') {
      if (found) {
        if (found.type === 'object') {
          mapStore.removeObject(found.item.id)
        } else {
          mapStore.removeTile(found.item.id)
        }
        toolStore.clearSelection()
        hoveredItem.value = null
        draw()
      }
      return
    }
    
    if (toolStore.activeTool === 'rotate') {
      if (found) {
        // Sélectionner l'élément avant rotation
        toolStore.selectObject(found.item.id)
        if (found.type === 'object') {
          mapStore.updateObject(found.item.id, { rotation: (found.item.rotation + 90) % 360 })
        } else {
          // For tiles, we need to update them (they don't have update method, so we replace)
          const newRotation = (found.item.rotation + 90) % 360
          mapStore.layers.tiles = mapStore.layers.tiles.filter(t => t.id !== found.item.id)
          mapStore.layers.tiles.push({ ...found.item, rotation: newRotation })
        }
        draw()
      }
      return
    }
    
    if (toolStore.activeTool === 'move') {
      // Mode déplacer : uniquement pour éléments déjà placés
      if (found) {
        // Calculer l'offset du curseur par rapport à l'image (en coordonnées monde)
        const imageData = imageCache.get(found.item.asset)
        if (imageData) {
          // Position de l'image en coordonnées monde (coin supérieur gauche)
          const imageWorldX = found.item.x * mapStore.tileSize + mapStore.gridOffsetX
          const imageWorldY = found.item.y * mapStore.tileSize + mapStore.gridOffsetY
          
          // Offset du curseur par rapport au coin supérieur gauche de l'image
          dragOffset.value = {
            x: worldX - imageWorldX,
            y: worldY - imageWorldY
          }
        } else {
          // Si l'image n'est pas encore chargée, utiliser un offset par défaut (centre)
          dragOffset.value = { x: 0, y: 0 }
        }
        
        // Sélectionner et commencer le drag
        toolStore.selectObject(found.item.id)
        draggedObject.value = found
        dragStartCoords.value = { x: coords.x, y: coords.y }
        isDragging.value = true
        draw()
        return
      }
      // Si pas d'élément trouvé en mode move : désélectionner et activer pan
      toolStore.clearSelection()
      hoveredItem.value = null
      isPanning.value = true
      isDragging.value = true
      dragStart.value = { x: event.clientX, y: event.clientY }
      dragStartCoords.value = { x: mapStore.gridOffsetX, y: mapStore.gridOffsetY }
      updateCursor()
      return
    }
    
    if (toolStore.activeTool === 'place') {
      // Mode placer : placer de nouveaux éléments si asset sélectionné
      if (selectedAsset.value) {
        let newItemId
        if (selectedAsset.value.category === 'tiles' || selectedAsset.value.category === '01.tiles') {
          mapStore.addTile(coords.x, coords.y, selectedAsset.value.path, 0)
          newItemId = mapStore.layers.tiles[mapStore.layers.tiles.length - 1].id
        } else {
          mapStore.addObject({
            type: selectedAsset.value.category,
            asset: selectedAsset.value.path,
            x: coords.x,
            y: coords.y,
            rotation: 0
          })
          newItemId = mapStore.layers.objects[mapStore.layers.objects.length - 1].id
        }
        // Sélectionner automatiquement le nouvel élément
        toolStore.selectObject(newItemId)
        draw()
        return
      }
      // Si pas d'asset sélectionné en mode place : désélectionner et activer pan
      toolStore.clearSelection()
      hoveredItem.value = null
      isPanning.value = true
      isDragging.value = true
      dragStart.value = { x: event.clientX, y: event.clientY }
      dragStartCoords.value = { x: mapStore.gridOffsetX, y: mapStore.gridOffsetY }
      updateCursor()
      return
    }
    
    // Pan mode: click on empty space (pas d'élément, pas d'asset)
    // Désélectionner et activer le pan
    toolStore.clearSelection()
    hoveredItem.value = null
    isPanning.value = true
    isDragging.value = true
    dragStart.value = { x: event.clientX, y: event.clientY }
    dragStartCoords.value = { x: mapStore.gridOffsetX, y: mapStore.gridOffsetY }
    updateCursor()
  } else if (event.button === 2) { // Right click - rotate
    event.preventDefault()
    const coords = getGridCoordinates(
      event.clientX,
      event.clientY,
      canvasRef.value,
      mapStore.tileSize,
      zoom.value,
      panX.value,
      panY.value,
      mapStore.gridOffsetX,
      mapStore.gridOffsetY
    )
    const found = findItemAtCoords(coords)
    if (found) {
      if (found.type === 'object') {
        mapStore.updateObject(found.item.id, { rotation: (found.item.rotation + 90) % 360 })
      } else {
        const newRotation = (found.item.rotation + 90) % 360
        mapStore.layers.tiles = mapStore.layers.tiles.filter(t => t.id !== found.item.id)
        mapStore.layers.tiles.push({ ...found.item, rotation: newRotation })
      }
      draw()
    }
  }
}

const handleMouseMove = (event) => {
  if (isDragging.value) {
    if (isPanning.value) {
      // Pan the grid (déplacer grille + éléments)
      const deltaX = (event.clientX - dragStart.value.x) / zoom.value
      const deltaY = (event.clientY - dragStart.value.y) / zoom.value
      mapStore.setGridOffset(
        dragStartCoords.value.x + deltaX,
        dragStartCoords.value.y + deltaY
      )
      draw()
    } else if (draggedObject.value && toolStore.activeTool === 'move') {
      // Move object - utiliser l'offset pour maintenir la position relative du curseur
      const rect = canvasRef.value.getBoundingClientRect()
      // Convertir la position du curseur en coordonnées monde
      const worldX = (event.clientX - rect.left - panX.value) / zoom.value
      const worldY = (event.clientY - rect.top - panY.value) / zoom.value
      
      // Soustraire l'offset pour obtenir la position du coin supérieur gauche de l'image
      const imageWorldX = worldX - dragOffset.value.x
      const imageWorldY = worldY - dragOffset.value.y
      
      // Convertir en coordonnées de grille (snap)
      const gridX = Math.round((imageWorldX - mapStore.gridOffsetX) / mapStore.tileSize)
      const gridY = Math.round((imageWorldY - mapStore.gridOffsetY) / mapStore.tileSize)
      
      // Vérifier si la position a changé
      if (gridX !== dragStartCoords.value.x || gridY !== dragStartCoords.value.y) {
        if (draggedObject.value.type === 'object') {
          mapStore.updateObject(draggedObject.value.item.id, { x: gridX, y: gridY })
        } else {
          // Update tile position
          const tile = draggedObject.value.item
          mapStore.layers.tiles = mapStore.layers.tiles.filter(t => t.id !== tile.id)
          mapStore.layers.tiles.push({ ...tile, x: gridX, y: gridY })
        }
        dragStartCoords.value = { x: gridX, y: gridY }
        draw()
      }
    }
  } else {
    // Détecter élément survolé (si pas en train de drag/pan)
    // Convertir les coordonnées écran en coordonnées monde pour vérifier toute la surface de l'image
    const rect = canvasRef.value.getBoundingClientRect()
    const worldX = (event.clientX - rect.left - panX.value) / zoom.value
    const worldY = (event.clientY - rect.top - panY.value) / zoom.value
    
    // Chercher un élément à ces coordonnées monde (vérifie toute la surface de l'image)
    const found = findItemAtWorldCoords(worldX, worldY)
    const newHoveredItem = found ? found.item.id : null
    
    if (newHoveredItem !== hoveredItem.value) {
      hoveredItem.value = newHoveredItem
      updateCursor()
      draw()
    }
  }
}

// Fonction pour mettre à jour le curseur CSS
const updateCursor = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  
  // Si on est en train de pan, utiliser grabbing
  if (isDragging.value && isPanning.value) {
    canvas.style.cursor = 'grabbing'
    return
  }
  
  if (hoveredItem.value) {
    // Élément déjà placé survolé
    if (toolStore.activeTool === 'move') {
      canvas.style.cursor = 'move' // 4 flèches
    } else if (toolStore.activeTool === 'delete') {
      canvas.style.cursor = 'not-allowed' // Croix rouge
    } else if (toolStore.activeTool === 'rotate') {
      canvas.style.cursor = 'alias' // Rotation
    } else if (toolStore.activeTool === 'place') {
      canvas.style.cursor = 'default' // Mode place, curseur normal même sur élément existant
    }
  } else {
    // Pas d'élément survolé - sur le fond de la grille
    if (toolStore.activeTool === 'place' && selectedAsset.value) {
      canvas.style.cursor = 'crosshair' // Prêt à placer
    } else {
      canvas.style.cursor = 'grab' // Prêt à déplacer la grille
    }
  }
}

const handleMouseUp = (event) => {
  if (event.button === 0) {
    isDragging.value = false
    isPanning.value = false
    draggedObject.value = null
    updateCursor()
  }
}

const handleWheel = (event) => {
  event.preventDefault()
  const delta = event.deltaY > 0 ? 0.9 : 1.1
  zoom.value = Math.max(0.1, Math.min(5, zoom.value * delta))
  draw()
}

const zoomIn = () => {
  zoom.value = Math.min(5, zoom.value * 1.2)
  draw()
}

const zoomOut = () => {
  zoom.value = Math.max(0.1, zoom.value / 1.2)
  draw()
}

const resetZoom = () => {
  zoom.value = 1
  panX.value = 0
  panY.value = 0
  mapStore.setGridOffset(0, 0)
  draw()
}

// Handle drag and drop from AssetPanel and asset selection
onMounted(() => {
  const canvas = canvasRef.value
  if (canvas) {
    canvas.addEventListener('dragover', (e) => {
      e.preventDefault()
    })

    canvas.addEventListener('drop', (e) => {
      e.preventDefault()
      const data = e.dataTransfer.getData('application/json')
      if (data) {
        const asset = JSON.parse(data)
        selectedAsset.value = asset
        const coords = getGridCoordinatesWithSnap(
          e.clientX,
          e.clientY,
          canvas,
          mapStore.tileSize,
          zoom.value,
          panX.value,
          panY.value,
          mapStore.gridOffsetX,
          mapStore.gridOffsetY
        )
        
        let newItemId
        if (asset.category === 'tiles' || asset.category === '01.tiles') {
          mapStore.addTile(coords.x, coords.y, asset.path, 0)
          newItemId = mapStore.layers.tiles[mapStore.layers.tiles.length - 1].id
        } else {
          mapStore.addObject({
            type: asset.category,
            asset: asset.path,
            x: coords.x,
            y: coords.y,
            rotation: 0
          })
          newItemId = mapStore.layers.objects[mapStore.layers.objects.length - 1].id
        }
        // Sélectionner automatiquement l'élément créé
        toolStore.selectObject(newItemId)
        draw()
      }
    })
  }
  
  // Listen for asset selection from AssetPanel
  window.addEventListener('asset-selected', (e) => {
    selectedAsset.value = e.detail
  })
})
</script>

<style scoped>
.canvas-grid {
  position: relative;
  width: 100%;
  height: 100%;
  background: #ffffff;
  overflow: hidden;
}

canvas {
  display: block;
  cursor: default;
}

canvas.grab-cursor {
  cursor: grab;
}

canvas.grabbing-cursor {
  cursor: grabbing;
}

.canvas-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 5px;
  align-items: center;
  background: rgba(45, 45, 45, 0.95);
  padding: 8px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.5);
  border: 1px solid var(--primary-color);
}

.canvas-controls button {
  padding: 5px 10px;
  background: var(--brown-medium);
  color: white;
  border: 1px solid var(--brown-light);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.canvas-controls button:hover {
  background: var(--brown-light);
  border-color: var(--primary-color);
}

.zoom-level {
  font-size: 12px;
  color: white;
  margin-left: 5px;
  font-weight: 500;
}
</style>
