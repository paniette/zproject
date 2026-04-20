/**
 * Export canvas utilitaire.
 *
 * `CanvasGrid` répond avec un PNG hors-écran (crop, transparence, sans grille).
 * Pas de capture de secours sur le canvas visible (éviterait grille + fond blanc).
 */

export const CANVAS_EXPORT_REQUEST = 'zproject:canvas-export-request'
export const CANVAS_EXPORT_RESPONSE = 'zproject:canvas-export-response'

/** Délai max : chargement images + crop peut prendre plusieurs secondes. */
const EXPORT_RESPONSE_TIMEOUT_MS = 45000

/**
 * Demande à `CanvasGrid` un export sans grille.
 * @returns {Promise<string>} dataURL
 */

export function requestCanvasExportWithoutGrid ({ mimeType = 'image/png', quality = 0.92 } = {}) {
  return new Promise((resolve, reject) => {
    const canvas =
      document.querySelector('canvas.map-editor-canvas') ||
      document.querySelector('.canvas-grid canvas') ||
      document.querySelector('canvas')
    if (!canvas) {
      reject(new Error('Canvas non trouvé'))
      return
    }

    let done = false
    const timeout = setTimeout(() => {
      if (done) return
      done = true
      window.removeEventListener(CANVAS_EXPORT_RESPONSE, onResp)
      // Ne pas appeler canvas.toDataURL() ici : ce serait la vue écran avec grille et fond blanc.
      reject(
        new Error(
          'Export de la carte trop long ou le canvas n’a pas répondu. Réessayez ; si le problème persiste, rechargez la page.'
        )
      )
    }, EXPORT_RESPONSE_TIMEOUT_MS)

    const onResp = (e) => {
      const detail = e?.detail || {}
      if (detail.error) {
        if (done) return
        done = true
        clearTimeout(timeout)
        window.removeEventListener(CANVAS_EXPORT_RESPONSE, onResp)
        const err = detail.error instanceof Error ? detail.error : new Error(String(detail.error?.message || detail.error))
        reject(err)
        return
      }
      const dataURL = detail.dataURL ?? detail.dataUrl
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
