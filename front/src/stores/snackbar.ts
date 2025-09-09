import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Anchor } from '@/types/vuetify-types.ts'

const DEFAULT_TIMEOUT = 3000

export const useSnackStore = defineStore(
  'snackbar',
  () => {
    const displayed = ref(false)
    const text = ref<string | null>(null)
    const type = ref<string | null>(null)
    const timeout = ref(DEFAULT_TIMEOUT)
    const location = ref<Anchor>('bottom')
    const icon = ref<string | null>(null)
    const closable = ref(true)

    function display({
      text: newText,
      type: newType,
      timeout: newTimeout = DEFAULT_TIMEOUT,
      location: newLocation = 'bottom',
      closable: newClosable = true,
      icon: newIcon = null
    }) {
      if (displayed.value) {
        // Hack to reset the timer when the snackbar is already displayed
        setTimeout(() => {
          timeout.value = 0
          display({
            text: newText,
            type: newType,
            timeout: newTimeout,
            location: newLocation,
            closable: newClosable,
            icon: newIcon
          })
        }, 0)
      } else {
        text.value = newText
        type.value = newType
        timeout.value = newTimeout
        location.value = newLocation as Anchor
        closable.value = newClosable
        displayed.value = true
        icon.value = newIcon
      }
    }

    return {
      displayed,
      text,
      type,
      timeout,
      location,
      icon,
      closable,
      display
    }
  },
  {
    persist: true
  }
)
