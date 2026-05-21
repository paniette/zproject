/**
 * Parse, validate and normalize JSON map data for import.
 */

export class MapImportError extends Error {
  constructor (code, message) {
    super(message)
    this.name = 'MapImportError'
    this.code = code
  }
}

/**
 * @param {string} text
 * @returns {object}
 */
export function parseMapJsonText (text) {
  if (!text || !String(text).trim()) {
    throw new MapImportError('empty', 'Empty JSON')
  }
  try {
    const data = JSON.parse(text)
    if (!data || typeof data !== 'object' || Array.isArray(data)) {
      throw new MapImportError('invalid_json', 'Root must be a JSON object')
    }
    return data
  } catch (e) {
    if (e instanceof MapImportError) throw e
    throw new MapImportError('invalid_json', 'Invalid JSON')
  }
}

/**
 * Read a File as text and parse JSON.
 * @param {File} file
 * @returns {Promise<object>}
 */
export function parseMapJsonFile (file) {
  return new Promise((resolve, reject) => {
    if (!file) {
      reject(new MapImportError('no_file', 'No file selected'))
      return
    }
    const reader = new FileReader()
    reader.onload = () => {
      try {
        resolve(parseMapJsonText(reader.result))
      } catch (e) {
        reject(e)
      }
    }
    reader.onerror = () => {
      reject(new MapImportError('read_error', 'Could not read file'))
    }
    reader.readAsText(file)
  })
}

/**
 * Validation error codes (i18n keys under importModal.errors.*).
 * @param {object} data
 * @returns {string[]}
 */
export function getImportValidationErrors (data) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    return ['invalidRoot']
  }
  const errors = []
  const name = typeof data.name === 'string' ? data.name.trim() : ''
  if (!name) errors.push('missingName')
  const grid = data.grid
  if (!grid || typeof grid !== 'object') {
    errors.push('missingGrid')
  } else {
    if (typeof grid.width !== 'number') errors.push('missingGridWidth')
    if (typeof grid.height !== 'number') errors.push('missingGridHeight')
  }
  if (!data.layers || typeof data.layers !== 'object') {
    errors.push('missingLayers')
  }
  return errors
}

/**
 * @param {object} data
 * @returns {boolean}
 */
export function validateImportedMap (data) {
  return getImportValidationErrors(data).length === 0
}

/**
 * Build payload for api.createMap (new id assigned server-side / localStorage).
 * pack may be null (carte multi-packs / export sans pack sélectionné).
 * @param {object} parsed
 * @param {string} username
 * @returns {object}
 */
export function prepareMapForImport (parsed, username) {
  const now = new Date().toISOString()
  const name = String(parsed.name).trim()
  const mapData = {
    name,
    pack: parsed.pack ?? null,
    grid: {
      width: parsed.grid.width,
      height: parsed.grid.height,
      tileSize: parsed.grid.tileSize ?? 32
    },
    layers: JSON.parse(JSON.stringify(parsed.layers)),
    gridOffsetX: parsed.gridOffsetX ?? 0,
    gridOffsetY: parsed.gridOffsetY ?? 0,
    metadata: {
      created: now,
      modified: now,
      author: username
    }
  }
  if (parsed.mission != null) {
    mapData.mission = JSON.parse(JSON.stringify(parsed.mission))
  }
  return mapData
}
