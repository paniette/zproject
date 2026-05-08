import { createI18n } from 'vue-i18n'
import fr from './locales/fr.json'
import en from './locales/en.json'
import de from './locales/de.json'
import es from './locales/es.json'

const STORAGE_KEY = 'zproject_locale'
export const SUPPORTED_LOCALES = ['fr', 'en', 'de', 'es']

function detectLocale () {
  if (typeof window === 'undefined') return 'fr'
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved && SUPPORTED_LOCALES.includes(saved)) return saved
  const nav = (navigator.language || navigator.userLanguage || 'fr').toLowerCase()
  if (nav.startsWith('en')) return 'en'
  if (nav.startsWith('de')) return 'de'
  if (nav.startsWith('es')) return 'es'
  return 'fr'
}

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: detectLocale(),
  fallbackLocale: 'fr',
  messages: { fr, en, de, es },
  missingWarn: false,
  fallbackWarn: false,
})
