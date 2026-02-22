import { ref } from 'vue'

export function useModal(initialState = false) {
  const isOpen = ref(initialState)

  const open = () => { isOpen.value = true }
  const close = () => { isOpen.value = false }
  const toggle = () => { isOpen.value = !isOpen.value }

  return { isOpen, open, close, toggle }
}

type ModalState<K extends string> = Record<K, boolean>

export function useModals<K extends string>(keys: K[]) {
  const modals = ref<ModalState<K>>(
    keys.reduce((acc, key) => ({ ...acc, [key]: false }), {} as ModalState<K>)
  )

  const open = (key: K) => { modals.value[key] = true }
  const close = (key: K) => { modals.value[key] = false }
  const toggle = (key: K) => { modals.value[key] = !modals.value[key] }
  const isOpen = (key: K) => modals.value[key]
  const closeAll = () => {
    keys.forEach(key => { modals.value[key] = false })
  }

  return { modals, open, close, toggle, isOpen, closeAll }
}
