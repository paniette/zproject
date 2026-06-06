import { useMapStore } from '@/stores/mapStore'

/**
 * Ouvre la boîte de dialogue d’impression / PDF (feuille mission A4).
 * Même comportement que le bouton « Imprimer / PDF » de la page Mission.
 */
export function printMissionPdf () {
  const root = document.getElementById('mission-print-root')
  if (!root) {
    return { ok: false, reason: 'no_root' }
  }
  const mapStore = useMapStore()
  const themeId = mapStore.mission?.pageTheme
  root.setAttribute('data-mission-theme', themeId || 'classic')
  window.print()
  return { ok: true }
}
