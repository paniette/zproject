/**
 * Fonds de page mission PDF (texture + bande décorative optionnelle).
 * Fichiers dans frontend/public/mission-assets/{theme}/ — mode statique OK.
 */

export const PAGE_BACKGROUNDS = {
  fantasy: [],
  classic: [
    { id: 'z2e', label: 'Zombicide 2E', bg: 'z2e-background.svg', assetDir: 'modern' },
  ],
  modern: [
    { id: 'z2e', label: 'Zombicide 2E', bg: 'z2e-background.svg' },
    { id: 'z2e-band-right', label: 'Zombicide 2E + barre droite', bg: 'z2e-background.svg', band: 'z2e-band.svg', bandSide: 'right' },
    { id: 'z2e-band-left', label: 'Zombicide 2E + barre gauche', bg: 'z2e-background.svg', band: 'z2e-band-left.svg', bandSide: 'left' },
    // { id: 'zc-washington', label: 'ZC Washington', bg: 'zc-washington-background.svg' },
    // { id: 'fort-hendrix', label: 'Fort Hendrix', bg: 'fort-hendrix-background.svg' },
  ],
  western: [],
  scifi:   [],
  night:   [],
}

/**
 * @param {string} theme
 * @param {string|null} id - id catalogue ou ancien nom de fichier bg
 */
export function findPageBackground (theme, id) {
  if (!theme || !id) return null
  const list = PAGE_BACKGROUNDS[theme] ?? []
  return list.find(b => b.id === id || b.bg === id) ?? null
}

/**
 * @returns {{ bg: string|null, band: string|null, bandSide: 'left'|'right'|null }}
 */
export function getPageBackgroundLayers (theme, id) {
  const entry = findPageBackground(theme, id)
  if (!entry) return { bg: null, band: null, bandSide: null }
  const base = `/mission-assets/${entry.assetDir ?? theme}`
  return {
    bg: entry.bg ? `${base}/${entry.bg}` : null,
    band: entry.band ? `${base}/${entry.band}` : null,
    bandSide: entry.bandSide ?? null,
  }
}
