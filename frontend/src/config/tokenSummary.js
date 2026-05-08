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
 * `label` peut être une chaîne (rétrocompatibilité) ou un objet { fr, en }.
 */
export const MERGED_GROUPS = [
  { pattern: /^objective/i,              key: 'Objective', label: { fr: 'Objectif',       en: 'Objective'   } },
  { pattern: /^(guard|garde|gardes)/i,   key: 'Guard',     label: { fr: 'Garde',          en: 'Guard'       } },
  { pattern: /^vault-door/i,             key: 'VaultDoor', label: { fr: 'Porte de Crypte', en: 'Vault Door'  } },
  { pattern: /^vault/i,                  key: 'Vault',     label: { fr: 'Crypte',         en: 'Vault'       } },
  { pattern: /^spawn/i,                  key: 'Spawn',     label: { fr: 'Apparition',     en: 'Spawn'       } },
  { pattern: /^zone.?invasion/i,         key: 'Invasion',  label: { fr: 'Apparition',     en: 'Invasion'    } },
  { pattern: /^(signal)/i,               key: 'Signal',    label: { fr: 'Signal',         en: 'Signal'      } },
  { pattern: /^(ladder|echelle|échelle)/i, key: 'Ladder',  label: { fr: 'Échelle',        en: 'Ladder'      } },
  { pattern: /^(chaudron|cauldron)/i,    key: 'Cauldron',  label: { fr: 'Chaudron',       en: 'Cauldron'    } },
]

/** Libellés personnalisés (sans fusion de clé). Le premier match gagne. */
export const LABEL_OVERRIDES = [
  { pattern: /^door-.*blue/i,  label: { fr: 'Porte bleue',  en: 'Blue door'   } },
  { pattern: /^door-.*green/i, label: { fr: 'Porte verte',  en: 'Green door'  } },
  { pattern: /^door-.*red/i,   label: { fr: 'Porte rouge',  en: 'Red door'    } },
  { pattern: /^signal/i,       label: { fr: 'Signal',       en: 'Signal'      } },
  { pattern: /^statue.?chi/i,  label: { fr: 'Statue',       en: 'Statue'      } },
]

/**
 * Whitelist : si non vide, seuls les tokens dont le nom correspond
 * à au moins un motif sont affichés (après exclusion).
 * Mettre [] pour tout afficher (hors exclusions).
 */
export const INCLUDED_NAME_PATTERNS = [
  // Mode blacklist : laisser vide pour tout inclure (hors EXCLUDED_*).
]
