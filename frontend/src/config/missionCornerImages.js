/**
 * Images décoratives de coin pour la page mission PDF.
 * Les fichiers sont dans frontend/public/mission-assets/{theme}/
 * et servis via URL directe — compatible mode statique.
 */

export const CORNER_IMAGES = {
  fantasy: [
    { id: 'blueAngleEE', label: 'Bleu – Eternal Empire', file: 'blueAngleEE.png' },
  ],
  classic: [],
  modern:  [],
  western: [],
  scifi:   [],
  night:   [],
}

/**
 * Retourne l'URL publique de l'image de coin, ou null si absente.
 * @param {string} theme  - id du gameType (ex: 'fantasy')
 * @param {string|null} file - nom du fichier (ex: 'blueAngleEE.png')
 */
export function getCornerImageUrl (theme, file) {
  if (!theme || !file) return null
  return `/mission-assets/${theme}/${file}`
}
