import { ref, type Ref } from 'vue'

interface AsyncStateResult<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  execute: () => Promise<T | null>
  reset: () => void
}

export function useAsyncState<T>(
  asyncFn: () => Promise<T>,
  initialValue?: T
): AsyncStateResult<T> {
  const data = ref<T | null>(initialValue ?? null) as Ref<T | null>
  const loading = ref(false)
  const error = ref<string | null>(null)

  const execute = async (): Promise<T | null> => {
    loading.value = true
    error.value = null
    try {
      const result = await asyncFn()
      data.value = result
      return result
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      return null
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    data.value = initialValue ?? null
    loading.value = false
    error.value = null
  }

  return { data, loading, error, execute, reset }
}

interface AsyncStateWithOptionsResult<T> extends AsyncStateResult<T> {
  onSuccess: (callback: (data: T) => void) => void
  onError: (callback: (error: string) => void) => void
}

export function useAsyncStateWithCallbacks<T>(
  asyncFn: () => Promise<T>,
  initialValue?: T
): AsyncStateWithOptionsResult<T> {
  const data = ref<T | null>(initialValue ?? null) as Ref<T | null>
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  let successCallback: ((data: T) => void) | null = null
  let errorCallback: ((error: string) => void) | null = null

  const execute = async (): Promise<T | null> => {
    loading.value = true
    error.value = null
    try {
      const result = await asyncFn()
      data.value = result
      if (successCallback) successCallback(result)
      return result
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error'
      error.value = errorMsg
      if (errorCallback) errorCallback(errorMsg)
      return null
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    data.value = initialValue ?? null
    loading.value = false
    error.value = null
  }

  const onSuccess = (callback: (data: T) => void) => {
    successCallback = callback
  }

  const onError = (callback: (error: string) => void) => {
    errorCallback = callback
  }

  return { data, loading, error, execute, reset, onSuccess, onError }
}
