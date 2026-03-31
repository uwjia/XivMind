export const formatFileSize = (bytes: number): string => {
  if (!bytes || bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(i > 0 ? 1 : 0)} ${units[i]}`
}

export const getDownloadStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    pending: 'Pending',
    downloading: 'Downloading',
    completed: 'Completed',
    failed: 'Failed'
  }
  return labels[status] || status
}

export const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString()
}
