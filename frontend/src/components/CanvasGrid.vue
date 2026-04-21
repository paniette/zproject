<template>
  <div class="canvas-grid">
    <Toolbar />
    <div v-if="mapStore.isPreviewMode" class="preview-banner" aria-live="polite">Aperçu — édition désactivée</div>
    <canvas
      ref="canvasRef"
      class="map-editor-canvas"
      @pointerdown="handlePointerDown"
      @pointermove="handlePointerMove"
      @pointerup="handlePointerUp"
      @pointercancel="handlePointerCancel"
      @wheel="handleWheel"
      @contextmenu.prevent
      :class="{ 'grab-cursor': isPanning || (!hoveredItem && !isDragging), 'grabbing-cursor': isDragging && isPanning, 'preview-canvas': mapStore.isPreviewMode }"
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useToolStore } from '@/stores/toolStore'
import { renderGrid, getGridCoordinates, getGridCoordinatesWithSnap } from '@/services/canvasRenderer'
import { CANVAS_EXPORT_REQUEST, CANVAS_EXPORT_RESPONSE } from '@/services/canvasExport'
import { collectUsedTilePairKeys, isTilePairLocked } from '@/utils/tilePairs'
import { boundsForImageOnGrid, unionBounds, expandBounds } from '@/utils/mapExportBounds'
import Toolbar from './Toolbar.vue'

const EXPORT_MARGIN_PX = 8

const mapStore = useMapStore()
const toolStore = useToolStore()

const usedTilePairKeys = computed(() => collectUsedTilePairKeys(mapStore.layers.tiles))

const canvasRef = ref(null)
const ctx = ref(null)

const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
const isDragging = ref(false)
const isPanning = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const selectedAsset = ref(null)

watch(
  () => mapStore.layers.tiles,
  () => {
    const a = selectedAsset.value
    if (!a) return
    if (isTilePairLocked(a.path, a.category, usedTilePairKeys.value)) {
      selectedAsset.value = null
      window.dispatchEvent(new CustomEvent('asset-selected', { detail: null }))
    }
  },
  { deep: true }
)

const draggedObject = ref(null)
const dragStartCoords = ref({ x: 0, y: 0 })
const dragOffset = ref({ x: 0, y: 0 }) // Offset du curseur par rapport à l'image au début du drag
const hoveredItem = ref(null)
/** compound undo : une entrée pour tout un drag déplacement */
const dragCompoundActive = ref(false)

/** Contact multi-touch : zoom pincement */
const activePointers = new Map()
const activeGesturePointerId = ref(null)
const isPinching = ref(false)
let pinchInitialDistance = 1
let pinchInitialZoom = 1

const imageCache = new Map() // Store: { image: Image, width: number, height: number }
const isDrawing = ref(false) // Flag to prevent concurrent draws
const gridInitialized = ref(false) // Flag pour savoir si la grille a été initialisée
/** Si true, le prochain draw n'affiche pas les lignes de grille (export PNG / capture mission). */
const hideGridForExport = ref(false)


onMounted(() => {
  const canvas = canvasRef.value
  if (canvas) {
    ctx.value = canvas.getContext('2d')
    resizeCanvas()
    draw()

    canvas.addEventListener('dragover', (e) => {
      e.preventDefault()
    })

    canvas.addEventListener('drop', (e) => {
      e.preventDefault()
      if (mapStore.isPreviewMode) return
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
          if (isTilePairLocked(asset.path, asset.category, usedTilePairKeys.value)) {
            return
          }
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
        toolStore.setTool('move')
        toolStore.selectObject(newItemId)
        draw()
        updateCursor()
      }
    })
  }

  window.addEventListener('resize', resizeCanvas)
  window.addEventListener(CANVAS_EXPORT_REQUEST, handleExportRequest)

  window.addEventListener('asset-selected', (e) => {
    selectedAsset.value = e.detail
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCanvas)
  window.removeEventListener(CANVAS_EXPORT_REQUEST, handleExportRequest)
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

/**
 * Quand l’onglet Carte est masqué (v-show), le conteneur du canvas a souvent 0×0 :
 * on prend la taille de `.editor-stack` pour garder un buffer dessinable (export / capture mission).
 */
function getCanvasTargetSize (canvas) {
  const container = canvas?.parentElement
  let w = container?.clientWidth ?? 0
  let h = container?.clientHeight ?? 0
  if (!w || !h) {
    const stack = typeof document !== 'undefined' ? document.querySelector('.editor-stack') : null
    if (stack) {
      w = stack.clientWidth || w
      h = stack.clientHeight || h
    }
  }
  if (!w || !h) {
    w = 800
    h = 600
  }
  return [w, h]
}

const resizeCanvas = () => {
  const canvas = canvasRef.value
  if (canvas) {
    const [w, h] = getCanvasTargetSize(canvas)
    canvas.width = w
    canvas.height = h
    
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
  if (!hideGridForExport.value) {
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
  }

  // Dessin séquentiel = ordre Z stable (dernier = au-dessus), aligné avec le hit-test au survol
  for (const tile of mapStore.layers.tiles) {
    await drawTile(tile)
  }
  for (const obj of mapStore.layers.objects) {
    await drawObject(obj)
  }

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

const waitForDrawIdle = async () => {
  for (let i = 0; i < 200; i++) {
    if (!isDrawing.value) return
    await new Promise((r) => requestAnimationFrame(r))
  }
}

const handleExportRequest = async (e) => {
  const { mimeType = 'image/png', quality = 0.92 } = e.detail || {}
  try {
    await waitForDrawIdle()
    const tiles = mapStore.layers.tiles || []
    const objects = mapStore.layers.objects || []
    if (!tiles.length && !objects.length) {
      throw new Error('Aucun élément sur la carte à capturer.')
    }

    const rawBounds = await computeWorldContentBounds()
    if (!rawBounds) {
      throw new Error('Impossible de calculer la zone de la carte (aucune image chargée).')
    }

    const b = expandBounds(rawBounds, EXPORT_MARGIN_PX)
    const outW = Math.max(1, Math.ceil(b.maxX - b.minX))
    const outH = Math.max(1, Math.ceil(b.maxY - b.minY))

    const off = document.createElement('canvas')
    off.width = outW
    off.height = outH
    const octx = off.getContext('2d')
    if (!octx) throw new Error('Contexte 2D indisponible pour l’export.')

    if (mimeType.includes('jpeg')) {
      octx.fillStyle = '#ffffff'
      octx.fillRect(0, 0, outW, outH)
    }

    octx.translate(-b.minX, -b.minY)

    for (const t of tiles) await drawTileToContext(octx, t)
    for (const o of objects) await drawObjectToContext(octx, o)

    const dataUrl = mimeType.includes('jpeg')
      ? off.toDataURL('image/jpeg', quality)
      : off.toDataURL(mimeType)

    window.dispatchEvent(new CustomEvent(CANVAS_EXPORT_RESPONSE, { detail: { dataURL: dataUrl } }))
  } catch (err) {
    window.dispatchEvent(new CustomEvent(CANVAS_EXPORT_RESPONSE, { detail: { error: err } }))
  }
}

function assetPathToSrc (path) {
  const baseUrl = import.meta.env.BASE_URL || ''
  if (path.startsWith('assets/') || path.startsWith('bgmapeditor_tiles/')) {
    return `${baseUrl}${path}`
  }
  return `${baseUrl}assets/${path}`
}

/** Chemins alternatifs si les fichiers ont été renommés (webp, frame, etc.). */
function alternateAssetPaths (assetPath) {
  if (!assetPath || typeof assetPath !== 'string') return []
  const a = assetPath.replace(/\\/g, '/')
  const alts = new Set()
  if (/\/r_0\.png$/i.test(a)) alts.add(a.replace(/\/r_0\.png$/i, '/r_0.webp'))
  if (/\/r_0\.webp$/i.test(a)) alts.add(a.replace(/\/r_0\.webp$/i, '/r_0.png'))
  if (/\/\d+[RV]\.png\/r_0\.(png|webp)$/i.test(a)) {
    alts.add(a.replace(/(\/\d+[RV])\.png\//i, '$1.webp/'))
  }
  alts.delete(a)
  return [...alts]
}

const loadImage = (assetPath) => {
  return new Promise((resolve) => {
    if (imageCache.has(assetPath)) {
      resolve(imageCache.get(assetPath))
      return
    }

    const pathsToTry = [assetPath, ...alternateAssetPaths(assetPath)].filter(
      (p, i, arr) => arr.indexOf(p) === i
    )

    const attempt = (index) => {
      if (index >= pathsToTry.length) {
        resolve(null)
        return
      }
      const path = pathsToTry[index]
      const img = new Image()
      img.onload = () => {
        const imageData = {
          image: img,
          width: img.width,
          height: img.height
        }
        imageCache.set(assetPath, imageData)
        resolve(imageData)
      }
      img.onerror = () => attempt(index + 1)
      img.src = assetPathToSrc(path)
    }
    attempt(0)
  })
}

async function computeWorldContentBounds () {
  const tiles = mapStore.layers.tiles || []
  const objects = mapStore.layers.objects || []
  const ts = mapStore.tileSize
  const gx = mapStore.gridOffsetX
  const gy = mapStore.gridOffsetY
  const boxes = []
  for (const tile of tiles) {
    const imageData = await loadImage(tile.asset)
    if (!imageData?.image) continue
    const x = tile.x * ts + gx
    const y = tile.y * ts + gy
    boxes.push(boundsForImageOnGrid(x, y, imageData.width, imageData.height, tile.rotation || 0))
  }
  for (const obj of objects) {
    const imageData = await loadImage(obj.asset)
    if (!imageData?.image) continue
    const x = obj.x * ts + gx
    const y = obj.y * ts + gy
    boxes.push(boundsForImageOnGrid(x, y, imageData.width, imageData.height, obj.rotation || 0))
  }
  if (!boxes.length) return null
  return unionBounds(boxes)
}

async function drawTileToContext (c, tile) {
  if (!c) return
  const imageData = await loadImage(tile.asset)
  if (imageData && imageData.image) {
    c.save()
    const img = imageData.image
    const imgWidth = imageData.width
    const imgHeight = imageData.height
    const x = tile.x * mapStore.tileSize + mapStore.gridOffsetX
    const y = tile.y * mapStore.tileSize + mapStore.gridOffsetY
    c.translate(x + imgWidth / 2, y + imgHeight / 2)
    c.rotate((tile.rotation * Math.PI) / 180)
    c.drawImage(img, -imgWidth / 2, -imgHeight / 2, imgWidth, imgHeight)
    c.restore()
  }
}

async function drawObjectToContext (c, obj) {
  if (!c) return
  const imageData = await loadImage(obj.asset)
  if (imageData && imageData.image) {
    c.save()
    const img = imageData.image
    const imgWidth = imageData.width
    const imgHeight = imageData.height
    const x = obj.x * mapStore.tileSize + mapStore.gridOffsetX
    const y = obj.y * mapStore.tileSize + mapStore.gridOffsetY
    c.translate(x + imgWidth / 2, y + imgHeight / 2)
    c.rotate((obj.rotation * Math.PI) / 180)
    c.drawImage(img, -imgWidth / 2, -imgHeight / 2, imgWidth, imgHeight)
    c.restore()
  }
}

const drawTile = async (tile) => {
  if (!ctx.value) return
  await drawTileToContext(ctx.value, tile)
}

const drawObject = async (obj) => {
  if (!ctx.value) return
  await drawObjectToContext(ctx.value, obj)
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
  // Dernier de la liste = au-dessus (même principe que le hit-test monde)
  let topObj = null
  for (const o of mapStore.layers.objects) {
    if (o.x === coords.x && o.y === coords.y) topObj = o
  }
  if (topObj) return { type: 'object', item: topObj }

  let topTile = null
  for (const t of mapStore.layers.tiles) {
    if (t.x === coords.x && t.y === coords.y) topTile = t
  }
  if (topTile) return { type: 'tile', item: topTile }

  return null
}

/** Boîte monde pour le survol : taille réelle si l'image est en cache, sinon une cellule (évite de cibler la tuile du dessous pendant le chargement). */
function worldBoundsForItemHit (item) {
  const ts = mapStore.tileSize
  const gx = mapStore.gridOffsetX
  const gy = mapStore.gridOffsetY
  const x = item.x * ts + gx
  const y = item.y * ts + gy
  const imageData = imageCache.get(item.asset)
  const w = imageData?.width ?? ts
  const h = imageData?.height ?? ts
  return { x, y, w, h }
}

function pointInWorldBounds (worldX, worldY, b) {
  return worldX >= b.x && worldX <= b.x + b.w && worldY >= b.y && worldY <= b.y + b.h
}

// Helper to find object/tile at world pixel coordinates (for hover detection)
const findItemAtWorldCoords = (worldX, worldY) => {
  // Objets au-dessus de toutes les tuiles ; au sein d'une couche, le dernier élément = au-dessus
  let topObj = null
  for (const obj of mapStore.layers.objects) {
    const b = worldBoundsForItemHit(obj)
    if (pointInWorldBounds(worldX, worldY, b)) topObj = obj
  }
  if (topObj) return { type: 'object', item: topObj }

  let topTile = null
  for (const tile of mapStore.layers.tiles) {
    const b = worldBoundsForItemHit(tile)
    if (pointInWorldBounds(worldX, worldY, b)) topTile = tile
  }
  if (topTile) return { type: 'tile', item: topTile }

  return null
}

const applyRightClickRotate = (clientX, clientY) => {
  if (mapStore.isPreviewMode) return
  const coords = getGridCoordinates(
    clientX,
    clientY,
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
      mapStore.updateTile(found.item.id, { rotation: (found.item.rotation + 90) % 360 })
    }
    draw()
  }
}

const applyPrimaryDown = (clientX, clientY) => {
  if (mapStore.isPreviewMode) {
    isPanning.value = true
    isDragging.value = true
    dragStart.value = { x: clientX, y: clientY }
    dragStartCoords.value = { x: mapStore.gridOffsetX, y: mapStore.gridOffsetY }
    return
  }
  const rect = canvasRef.value.getBoundingClientRect()
  const worldX = (clientX - rect.left - panX.value) / zoom.value
  const worldY = (clientY - rect.top - panY.value) / zoom.value

  let found = findItemAtWorldCoords(worldX, worldY)

  if (!found && hoveredItem.value) {
    const obj = mapStore.layers.objects.find(o => o.id === hoveredItem.value)
    const tile = obj ? null : mapStore.layers.tiles.find(t => t.id === hoveredItem.value)
    if (obj || tile) {
      found = { type: obj ? 'object' : 'tile', item: obj || tile }
    }
  }

  const coords = getGridCoordinatesWithSnap(
    clientX,
    clientY,
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
      toolStore.selectObject(found.item.id)
      if (found.type === 'object') {
        mapStore.updateObject(found.item.id, { rotation: (found.item.rotation + 90) % 360 })
      } else {
        mapStore.updateTile(found.item.id, { rotation: (found.item.rotation + 90) % 360 })
      }
      draw()
    }
    return
  }

  if (toolStore.activeTool === 'move') {
    if (found) {
      const imageData = imageCache.get(found.item.asset)
      if (imageData) {
        const imageWorldX = found.item.x * mapStore.tileSize + mapStore.gridOffsetX
        const imageWorldY = found.item.y * mapStore.tileSize + mapStore.gridOffsetY
        dragOffset.value = {
          x: worldX - imageWorldX,
          y: worldY - imageWorldY
        }
      } else {
        dragOffset.value = { x: 0, y: 0 }
      }

      mapStore.beginCompound()
      dragCompoundActive.value = true
      toolStore.selectObject(found.item.id)
      draggedObject.value = found
      dragStartCoords.value = { x: coords.x, y: coords.y }
      isDragging.value = true
      draw()
      return
    }
    toolStore.clearSelection()
    hoveredItem.value = null
    isPanning.value = true
    isDragging.value = true
    dragStart.value = { x: clientX, y: clientY }
    dragStartCoords.value = { x: mapStore.gridOffsetX, y: mapStore.gridOffsetY }
    updateCursor()
    return
  }

  if (toolStore.activeTool === 'place') {
    if (selectedAsset.value) {
      let newItemId
      if (selectedAsset.value.category === 'tiles' || selectedAsset.value.category === '01.tiles') {
        if (isTilePairLocked(selectedAsset.value.path, selectedAsset.value.category, usedTilePairKeys.value)) {
          return
        }
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
      toolStore.selectObject(newItemId)
      draw()
      return
    }
    toolStore.clearSelection()
    hoveredItem.value = null
    isPanning.value = true
    isDragging.value = true
    dragStart.value = { x: clientX, y: clientY }
    dragStartCoords.value = { x: mapStore.gridOffsetX, y: mapStore.gridOffsetY }
    updateCursor()
    return
  }

  toolStore.clearSelection()
  hoveredItem.value = null
  isPanning.value = true
  isDragging.value = true
  dragStart.value = { x: clientX, y: clientY }
  dragStartCoords.value = { x: mapStore.gridOffsetX, y: mapStore.gridOffsetY }
  updateCursor()
}

const applyPrimaryMove = (clientX, clientY) => {
  if (mapStore.isPreviewMode && isDragging.value && isPanning.value) {
    const deltaX = (clientX - dragStart.value.x) / zoom.value
    const deltaY = (clientY - dragStart.value.y) / zoom.value
    mapStore.setGridOffset(
      dragStartCoords.value.x + deltaX,
      dragStartCoords.value.y + deltaY
    )
    draw()
    return
  }
  if (isDragging.value) {
    if (isPanning.value) {
      const deltaX = (clientX - dragStart.value.x) / zoom.value
      const deltaY = (clientY - dragStart.value.y) / zoom.value
      mapStore.setGridOffset(
        dragStartCoords.value.x + deltaX,
        dragStartCoords.value.y + deltaY
      )
      draw()
    } else if (draggedObject.value && toolStore.activeTool === 'move') {
      const rect = canvasRef.value.getBoundingClientRect()
      const worldX = (clientX - rect.left - panX.value) / zoom.value
      const worldY = (clientY - rect.top - panY.value) / zoom.value

      const imageWorldX = worldX - dragOffset.value.x
      const imageWorldY = worldY - dragOffset.value.y

      const gridX = Math.round((imageWorldX - mapStore.gridOffsetX) / mapStore.tileSize)
      const gridY = Math.round((imageWorldY - mapStore.gridOffsetY) / mapStore.tileSize)

      if (gridX !== dragStartCoords.value.x || gridY !== dragStartCoords.value.y) {
        if (draggedObject.value.type === 'object') {
          mapStore.updateObject(draggedObject.value.item.id, { x: gridX, y: gridY })
        } else {
          mapStore.updateTile(draggedObject.value.item.id, { x: gridX, y: gridY })
        }
        dragStartCoords.value = { x: gridX, y: gridY }
        draw()
      }
    }
  } else {
    const rect = canvasRef.value.getBoundingClientRect()
    const worldX = (clientX - rect.left - panX.value) / zoom.value
    const worldY = (clientY - rect.top - panY.value) / zoom.value

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

const applyPrimaryUp = () => {
  if (dragCompoundActive.value) {
    mapStore.endCompound()
    dragCompoundActive.value = false
  }
  isDragging.value = false
  isPanning.value = false
  draggedObject.value = null
  updateCursor()
}

function releaseGestureCapture () {
  const canvas = canvasRef.value
  const id = activeGesturePointerId.value
  if (canvas && id != null) {
    try {
      if (canvas.hasPointerCapture(id)) canvas.releasePointerCapture(id)
    } catch (_) {}
  }
  activeGesturePointerId.value = null
}

function endPinchMonoGesture () {
  releaseGestureCapture()
  if (dragCompoundActive.value) {
    mapStore.endCompound()
    dragCompoundActive.value = false
  }
  isDragging.value = false
  isPanning.value = false
  draggedObject.value = null
  updateCursor()
}

function updatePinchZoomFromPointers () {
  if (activePointers.size < 2) return
  const pts = [...activePointers.values()]
  const d = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y) || 1
  const ratio = d / pinchInitialDistance
  zoom.value = Math.max(0.1, Math.min(5, pinchInitialZoom * ratio))
  draw()
}

const handlePointerDown = (e) => {
  const canvas = canvasRef.value
  if (!canvas) return

  activePointers.set(e.pointerId, { x: e.clientX, y: e.clientY })

  if (activePointers.size === 2) {
    endPinchMonoGesture()
    const pts = [...activePointers.values()]
    pinchInitialDistance = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y) || 1
    pinchInitialZoom = zoom.value
    isPinching.value = true
    e.preventDefault()
    return
  }

  if (isPinching.value) {
    e.preventDefault()
    return
  }

  if (e.pointerType === 'mouse' && e.button === 2) {
    applyRightClickRotate(e.clientX, e.clientY)
    e.preventDefault()
    return
  }

  if (e.button !== 0) return

  applyPrimaryDown(e.clientX, e.clientY)

  if (isDragging.value) {
    activeGesturePointerId.value = e.pointerId
    try {
      canvas.setPointerCapture(e.pointerId)
    } catch (_) {}
  }
  e.preventDefault()
}

const handlePointerMove = (e) => {
  activePointers.set(e.pointerId, { x: e.clientX, y: e.clientY })

  if (isPinching.value && activePointers.size >= 2) {
    updatePinchZoomFromPointers()
    e.preventDefault()
    return
  }

  if (activeGesturePointerId.value != null && e.pointerId !== activeGesturePointerId.value) {
    return
  }

  applyPrimaryMove(e.clientX, e.clientY)
  if (isDragging.value) e.preventDefault()
}

const handlePointerUp = (e) => {
  activePointers.delete(e.pointerId)

  if (isPinching.value && activePointers.size < 2) {
    isPinching.value = false
  }

  const gestureId = activeGesturePointerId.value
  if (gestureId != null && e.pointerId === gestureId) {
    releaseGestureCapture()
    applyPrimaryUp()
  }
}

const handlePointerCancel = (e) => {
  handlePointerUp(e)
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
  touch-action: none;
}

canvas.grab-cursor {
  cursor: grab;
}

canvas.grabbing-cursor {
  cursor: grabbing;
}

.preview-banner {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  padding: 6px 12px;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  background: color-mix(in srgb, var(--primary-color) 35%, #1a1a1a);
  color: #fff;
  pointer-events: none;
}

.preview-canvas {
  opacity: 0.98;
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

@media (max-width: 768px) {
  .canvas-controls {
    top: max(8px, env(safe-area-inset-top, 0px));
    right: max(8px, env(safe-area-inset-right, 0px));
    flex-wrap: wrap;
    max-width: min(200px, calc(100vw - 16px));
  }

  .canvas-controls button {
    min-width: 44px;
    min-height: 44px;
    padding: 8px 12px;
    font-size: 16px;
  }

  .zoom-level {
    width: 100%;
    margin-left: 0;
    margin-top: 4px;
    text-align: center;
  }
}
</style>
