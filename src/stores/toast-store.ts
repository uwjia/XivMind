import { defineStore } from 'pinia'
import { ref } from 'vue'

type ToastType = 'loading' | 'success' | 'error' | 'info'

export const useToastStore = defineStore('toast', () => {
  const visible = ref<boolean>(false)
  const message = ref<string>('')
  const type = ref<ToastType>('loading')
  const timeoutId = ref<number | null>(null)

  const showToast = (msg: string, toastType: ToastType = 'loading', duration: number = 3000) => {
    visible.value = true
    message.value = msg
    type.value = toastType

    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
    }

    if (duration > 0) {
      timeoutId.value = setTimeout(() => {
        hideToast()
      }, duration) as unknown as number
    }
  }

  const hideToast = () => {
    visible.value = false
    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
      timeoutId.value = null
    }
  }

  const showLoading = (msg: string = 'Loading...', duration: number = 0) => {
    showToast(msg, 'loading', duration)
  }

  const showSuccess = (msg: string = 'Success!', duration: number = 3000) => {
    showToast(msg, 'success', duration)
  }

  const showError = (msg: string = 'Error!', duration: number = 3000) => {
    showToast(msg, 'error', duration)
  }

  const showInfo = (msg: string = 'Info', duration: number = 3000) => {
    showToast(msg, 'info', duration)
  }

  return {
    visible,
    message,
    type,
    showToast,
    hideToast,
    showLoading,
    showSuccess,
    showError,
    showInfo
  }
})
