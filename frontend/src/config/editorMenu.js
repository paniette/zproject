import { config } from '@/config'

/**
 * Visibilité des contrôles « avancés » du menu (JSON, XML, Versions, Aperçu, export image, Thème, Utilisateur, uploads,
 * panneau Propriétés, indicateur Modifié/Enregistré à côté du titre).
 *
 * - **Dev local** : laissez tout à `true` (ou `USE_MINIMAL_MENU` à `false`).
 * - **Production** : passez les entrées à `false`, ou activez `USE_MINIMAL_MENU` / la variable d’environnement.
 *
 * Les uploads restent aussi désactivés si `config.staticMode` (pas d’API Django).
 *
 * Variable Vite optionnelle : `VITE_EDITOR_MINIMAL_MENU=true` au build → même effet que `USE_MINIMAL_MENU`
 * sans modifier ce fichier.
 */

export const USE_MINIMAL_MENU = true

export const editorMenuVisibility = {
  themeSelector: true,
  userSelector: true,
  preview: true,
  exportImage: true,
  propertyPanel: true,
  saveStatus: true,
  exportJson: true,
  exportXml: true,
  versions: true,
  uploadZip: true,
  uploadElement: true
}

export function getEditorMenuVisibility () {
  const envMinimal = import.meta.env.VITE_EDITOR_MINIMAL_MENU === 'true'
  const minimal = USE_MINIMAL_MENU || envMinimal
  const base = minimal
    ? {
        themeSelector: false,
        userSelector: false,
        preview: false,
        exportImage: false,
        propertyPanel: false,
        saveStatus: false,
        exportJson: false,
        exportXml: false,
        versions: false,
        uploadZip: false,
        uploadElement: false
      }
    : { ...editorMenuVisibility }

  return {
    ...base,
    uploadZip: base.uploadZip && !config.staticMode,
    uploadElement: base.uploadElement && !config.staticMode
  }
}
