/**
 * Configuration for the application
 * Set STATIC_MODE to true to use static packs index instead of API
 */
export const STATIC_MODE = import.meta.env.VITE_STATIC_MODE === 'true' || false

export const config = {
  staticMode: STATIC_MODE,
  packsIndexPath: '/packs-index.json'
}
