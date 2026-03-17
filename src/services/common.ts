import { API_BASE_URL } from './config'

export interface MessageResponse {
  message: string
  success: boolean
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}/api${endpoint}`
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      console.error('Network error:', error.message)
      throw new Error('Network error: Unable to connect to server')
    }
    throw error
  }
}
