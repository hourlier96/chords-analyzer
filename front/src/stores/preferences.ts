import { ref } from 'vue'
import { defineStore } from 'pinia'
import { defaultLocale } from '@/../i18n/index.js'
import { i18n } from '@/main.ts'

export const usePreferencesStore = defineStore(
  'preferences',
  () => {
    const isDark = ref(true)
    const lang = ref(defaultLocale)

    function toggleTheme(theme) {
      isDark.value = !isDark.value
      theme.change(isDark.value ? 'customDarkTheme' : 'customLightTheme')
    }

    function setLang(newLang: string) {
      lang.value = newLang
      i18n.global.locale.value = newLang
    }

    return { isDark, lang, toggleTheme, setLang }
  },
  {
    persist: true
  }
)
