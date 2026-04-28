/**
 * Configuration du résumé des jetons posés sur la carte (encart page mission).
 * Chaque jeton dans layers.objects a : { type, asset, x, y, rotation }.
 * Le champ `type` correspond à la catégorie du pack (ex. '04.other tokens').
 * Le nom du fichier (sans extension) sert de clé pour le filtrage.
 */

/** Catégories entières à ignorer (valeur de obj.type). */
export const EXCLUDED_CATEGORIES = [
  '01.tiles',
  '05.zombies',
]

/** Motifs exclus sur le nom de fichier du token (sans extension). */
export const EXCLUDED_NAME_PATTERNS = [
  /^invasion/i,
  /^numbered.?zone/i,
  /^exit/i,
  /^start/i,
]

/**
 * Groupes de fusion : plusieurs noms → 1 seule entrée + label affiché.
 * La première occurrence fournit l'image.
 */
export const MERGED_GROUPS = [
  { pattern: /^objective/i, key: 'Objective', label: 'Objectif' },
  { pattern: /^(guard|garde|gardes)/i, key: 'Guard', label: 'Garde' },
  { pattern: /^vault-door/i, key: 'VaultDoor', label: 'Porte de Crypte' },
  { pattern: /^vault/i,      key: 'Vault',     label: 'Crypte' },
  { pattern: /^spawn/i,      key: 'Spawn',     label: 'Apparition' },
  { pattern: /^zone.?invasion/i, key: 'Invasion', label: 'Apparition' },
  // Éléments à afficher « petit » comme les portes dans l'encart
  { pattern: /^(signal)/i, key: 'Signal', label: 'Signal' },
  { pattern: /^(ladder|echelle|échelle)/i, key: 'Ladder', label: 'Échelle' },
  { pattern: /^(chaudron|cauldron)/i, key: 'Cauldron', label: 'Chaudron' },
]

/** Libellés personnalisés (sans fusion de clé). Le premier match gagne. */
export const LABEL_OVERRIDES = [
  { pattern: /^door-.*blue/i, label: 'Porte bleue' },
  { pattern: /^door-.*green/i, label: 'Porte verte' },
  { pattern: /^door-.*red/i, label: 'Porte rouge' },
  { pattern: /^signal/i, label: 'Signal' },
  { pattern: /^statue.?chi/i, label: 'Statue' },
]

/**
 * Whitelist : si non vide, seuls les tokens dont le nom correspond
 * à au moins un motif sont affichés (après exclusion).
 * Mettre [] pour tout afficher (hors exclusions).
 */
export const INCLUDED_NAME_PATTERNS = [
  // Mode blacklist : laisser vide pour tout inclure (hors EXCLUDED_*).
]
