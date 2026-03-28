/**
 * Configuration for the application
 * Set STATIC_MODE to false to disable static mode (default: true)
 */
// Par défaut, STATIC_MODE est true sauf si explicitement défini à 'false'
export const STATIC_MODE = import.meta.env.VITE_STATIC_MODE !== 'false'

export const config = {
  staticMode: STATIC_MODE,
  packsIndexPath: './packs-index.json'  // Chemin relatif explicite depuis editor.html
}
