/**
 * Export canvas utilitaire.
 *
 * L’en-tête peut demander un export "sans grille" si le canvas supporte un flux dédié.
 * Si non disponible, on fallback sur `canvas.toDataURL()`.
 */

export const CANVAS_EXPORT_REQUEST = 'zproject:canvas-export-request'
export const CANVAS_EXPORT_RESPONSE = 'zproject:canvas-export-response'

/**
 * Demande à `CanvasGrid` un export (ex. sans grille), sinon fallback.
 * @returns {Promise<string>} dataURL
 */
export function requestCanvasExportWithoutGrid ({ mimeType = 'image/png', quality = 0.92 } = {}) {
  return new Promise((resolve, reject) => {
    const canvas = document.querySelector('canvas')
    if (!canvas) {
      reject(new Error('Canvas non trouvé'))
      return
    }

    let done = false
    const timeout = setTimeout(() => {
      if (done) return
      done = true
      // fallback
      try {
        resolve(canvas.toDataURL(mimeType, quality))
      } catch (e) {
        reject(e)
      }
    }, 900)

    const onResp = (e) => {
      const detail = e?.detail || {}
      const dataURL = detail.dataURL
      if (!dataURL || typeof dataURL !== 'string') return
      if (done) return
      done = true
      clearTimeout(timeout)
      window.removeEventListener(CANVAS_EXPORT_RESPONSE, onResp)
      resolve(dataURL)
    }

    window.addEventListener(CANVAS_EXPORT_RESPONSE, onResp)
    window.dispatchEvent(new CustomEvent(CANVAS_EXPORT_REQUEST, { detail: { mimeType, quality } }))
  })
}

