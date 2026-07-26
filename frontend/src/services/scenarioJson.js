/**
 * Export / import scénario JSON (carte + mission).
 */

export function buildMapPayload (mapStore) {
  return {
    id: mapStore.currentMapId || undefined,
    name: mapStore.mapName,
    pack: mapStore.currentPack,
    grid: {
      width: mapStore.gridSize.width,
      height: mapStore.gridSize.height,
      tileSize: mapStore.tileSize
    },
    layers: JSON.parse(JSON.stringify(mapStore.layers)),
    gridOffsetX: mapStore.gridOffsetX,
    gridOffsetY: mapStore.gridOffsetY,
    mission: JSON.parse(JSON.stringify(mapStore.mission))
  }
}

function downloadTextFile (filename, text, mime) {
  const blob = new Blob([text], { type: mime || 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

export function exportScenarioJson (mapStore) {
  const payload = buildMapPayload(mapStore)
  const name = (mapStore.mapName || 'scenario').replace(/[^\w\-]+/g, '_')
  downloadTextFile(
    `${name}_${new Date().toISOString().slice(0, 10)}.json`,
    JSON.stringify(payload, null, 2),
    'application/json'
  )
}
