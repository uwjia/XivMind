export const getApiBaseUrl = (): string => {
  const isElectron = typeof window !== 'undefined' && window.electronAPI !== undefined
  const isFileProtocol = typeof window !== 'undefined' && window.location?.protocol === 'file:'
  return (isElectron || isFileProtocol) ? 'http://localhost:8000' : ''
}

export const API_BASE_URL = getApiBaseUrl()
