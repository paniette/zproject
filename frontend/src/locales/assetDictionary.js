/**
 * Dictionnaire bilingue (FR/EN) pour les noms de fichiers d'assets et catégories de packs.
 * Utilisé par MissionPagePreview et AssetPanel pour afficher des libellés lisibles.
 */

/** Catégories de pack (dossiers) → label FR/EN */
const CATEGORY_LABELS = [
  { pattern: /^01[\.\-_ ]?tiles?/i,      fr: 'Tuiles',         en: 'Tiles' },
  { pattern: /^02[\.\-_ ]?char/i,        fr: 'Personnages',    en: 'Characters' },
  { pattern: /^03[\.\-_ ]?obj/i,         fr: 'Objectifs',      en: 'Objectives' },
  { pattern: /^04[\.\-_ ]?other/i,       fr: 'Autres jetons',  en: 'Other tokens' },
  { pattern: /^04[\.\-_ ]?token/i,       fr: 'Jetons',         en: 'Tokens' },
  { pattern: /^05[\.\-_ ]?zombie/i,      fr: 'Zombies',        en: 'Zombies' },
  { pattern: /^06[\.\-_ ]?spawn/i,       fr: 'Points de pop',  en: 'Spawn points' },
  { pattern: /^07[\.\-_ ]?door/i,        fr: 'Portes',         en: 'Doors' },
  { pattern: /^08[\.\-_ ]?trap/i,        fr: 'Pièges',         en: 'Traps' },
  { pattern: /^09[\.\-_ ]?misc/i,        fr: 'Divers',         en: 'Miscellaneous' },
]

/** Noms de fichiers d'assets → label FR/EN (correspondance par motif regex) */
const ASSET_LABELS = [
  { pattern: /^objective/i,                  fr: 'Objectif',       en: 'Objective' },
  { pattern: /^(guard|garde|gardes)/i,       fr: 'Garde',          en: 'Guard' },
  { pattern: /^vault-door/i,                 fr: 'Porte de Crypte', en: 'Vault Door' },
  { pattern: /^vault/i,                      fr: 'Crypte',         en: 'Vault' },
  { pattern: /^spawn/i,                      fr: 'Apparition',     en: 'Spawn' },
  { pattern: /^zone.?invasion/i,             fr: 'Apparition',     en: 'Invasion' },
  { pattern: /^(signal)/i,                   fr: 'Signal',         en: 'Signal' },
  { pattern: /^(ladder|echelle|échelle)/i,   fr: 'Échelle',        en: 'Ladder' },
  { pattern: /^(chaudron|cauldron)/i,        fr: 'Chaudron',       en: 'Cauldron' },
  { pattern: /^door-.*blue/i,               fr: 'Porte bleue',    en: 'Blue door' },
  { pattern: /^door-.*green/i,              fr: 'Porte verte',    en: 'Green door' },
  { pattern: /^door-.*red/i,               fr: 'Porte rouge',    en: 'Red door' },
  { pattern: /^door/i,                      fr: 'Porte',          en: 'Door' },
  { pattern: /^statue.?chi/i,               fr: 'Statue',         en: 'Statue' },
  { pattern: /^statue/i,                    fr: 'Statue',         en: 'Statue' },
  { pattern: /^zombie/i,                    fr: 'Zombie',         en: 'Zombie' },
  { pattern: /^survivor/i,                  fr: 'Survivant',      en: 'Survivor' },
  { pattern: /^hero/i,                      fr: 'Héros',          en: 'Hero' },
  { pattern: /^abomination/i,               fr: 'Abomination',    en: 'Abomination' },
  { pattern: /^necro/i,                     fr: 'Nécromant',      en: 'Necromancer' },
  { pattern: /^runner/i,                    fr: 'Coureur',        en: 'Runner' },
  { pattern: /^walker/i,                    fr: 'Marcheur',       en: 'Walker' },
  { pattern: /^fatty/i,                     fr: 'Gros',           en: 'Fatty' },
  { pattern: /^chest/i,                     fr: 'Coffre',         en: 'Chest' },
  { pattern: /^altar/i,                     fr: 'Autel',          en: 'Altar' },
  { pattern: /^potion/i,                    fr: 'Potion',         en: 'Potion' },
  { pattern: /^weapon/i,                    fr: 'Arme',           en: 'Weapon' },
  { pattern: /^torch/i,                     fr: 'Torche',         en: 'Torch' },
  { pattern: /^trap/i,                      fr: 'Piège',          en: 'Trap' },
  { pattern: /^fountain/i,                  fr: 'Fontaine',       en: 'Fountain' },
  { pattern: /^portal/i,                    fr: 'Portail',        en: 'Portal' },
  { pattern: /^key/i,                       fr: 'Clé',            en: 'Key' },
  { pattern: /^scroll/i,                    fr: 'Parchemin',      en: 'Scroll' },
  { pattern: /^shield/i,                    fr: 'Bouclier',       en: 'Shield' },
  { pattern: /^crown/i,                     fr: 'Couronne',       en: 'Crown' },
]

/**
 * Traduit un nom de fichier d'asset (sans extension) en label lisible selon la locale.
 * @param {string} filename - Nom du fichier sans extension
 * @param {string} locale - 'fr' ou 'en'
 * @returns {string}
 */
export function translateAssetLabel (filename, locale) {
  if (!filename) return ''
  const lang = locale === 'en' ? 'en' : 'fr'
  const entry = ASSET_LABELS.find(e => e.pattern.test(filename))
  if (entry) return entry[lang]
  return capitalizeWords(filename.replace(/-/g, ' '))
}

/**
 * Traduit un nom de catégorie de pack en label lisible selon la locale.
 * @param {string} category - Nom brut de la catégorie (ex. '01.tiles')
 * @param {string} locale - 'fr' ou 'en'
 * @returns {string}
 */
export function translateCategoryName (category, locale) {
  if (!category) return ''
  const lang = locale === 'en' ? 'en' : 'fr'
  const entry = CATEGORY_LABELS.find(e => e.pattern.test(category))
  if (entry) return entry[lang]
  return capitalizeWords(category.replace(/^\d+[\.\-_ ]?/, '').replace(/[-_]/g, ' '))
}

/**
 * Récupère le label FR ou EN depuis un objet `{ fr, en }` ou une chaîne brute.
 * @param {string|{fr:string,en:string}} label
 * @param {string} locale
 * @returns {string}
 */
export function resolveLabel (label, locale) {
  if (!label) return ''
  if (typeof label === 'object') {
    const lang = locale === 'en' ? 'en' : 'fr'
    return label[lang] || label.fr || label.en || ''
  }
  return String(label)
}

function capitalizeWords (str) {
  return str
    .split(' ')
    .map(w => w ? w[0].toUpperCase() + w.slice(1) : w)
    .join(' ')
}
