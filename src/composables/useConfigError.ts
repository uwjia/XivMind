const configErrorPatterns = [
  /api[_-]?key/i,
  /not configured/i,
  /missing.*key/i,
  /key is required/i,
  /authentication/i,
  /unauthorized/i,
  /invalid.*key/i,
  /no provider/i,
  /provider not available/i,
  /400 bad request/i,
  /401/i,
  /403 forbidden/i,
  /connection refused/i,
  /localhost.*11434/i,
  /ollama/i,
  /ECONNREFUSED/i,
  /network error/i,
  /failed to fetch/i,
  /request failed/i,
  /connection error/i,
  /timeout/i,
  /ETIMEDOUT/i
]

export function useConfigError() {
  const isConfigError = (errorMsg: string): boolean => {
    if (!errorMsg) return false
    return configErrorPatterns.some(pattern => pattern.test(errorMsg))
  }

  const getConfigErrorType = (errorMsg: string): 'api_key' | 'connection' | 'provider' | 'unknown' => {
    if (!errorMsg) return 'unknown'
    
    if (/api[_-]?key|not configured|missing.*key|key is required|invalid.*key|unauthorized|401|403/i.test(errorMsg)) {
      return 'api_key'
    }
    
    if (/connection refused|localhost.*11434|ollama|ECONNREFUSED|network error|failed to fetch|connection error|timeout|ETIMEDOUT/i.test(errorMsg)) {
      return 'connection'
    }
    
    if (/no provider|provider not available/i.test(errorMsg)) {
      return 'provider'
    }
    
    return 'unknown'
  }

  const getConfigErrorHint = (errorMsg: string): string => {
    const type = getConfigErrorType(errorMsg)
    
    switch (type) {
      case 'api_key':
        return 'Please check your API key configuration in Settings.'
      case 'connection':
        return 'Unable to connect to the LLM service. Please check if the service is running.'
      case 'provider':
        return 'No LLM provider is configured. Please set up a provider in Settings.'
      default:
        return 'An error occurred. Please check your configuration in Settings.'
    }
  }

  return { 
    isConfigError, 
    getConfigErrorType, 
    getConfigErrorHint 
  }
}
