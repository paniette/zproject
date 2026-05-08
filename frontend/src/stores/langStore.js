import { defineStore } from 'pinia'
import { i18n, SUPPORTED_LOCALES } from '@/i18n'

const STORAGE_KEY = 'zproject_locale'

export const useLangStore = defineStore('lang', {
  state: () => ({
    locale: i18n.global.locale.value
  }),
  actions: {
    setLocale (lang) {
      if (!SUPPORTED_LOCALES.includes(lang)) return
      this.locale = lang
      i18n.global.locale.value = lang
      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, lang)
      }
    },
    cycle () {
      const idx = SUPPORTED_LOCALES.indexOf(this.locale)
      const next = SUPPORTED_LOCALES[(idx + 1) % SUPPORTED_LOCALES.length]
      this.setLocale(next)
    }
  }
})
