export interface Note {
  id: string
  content: string
  createdAt: string
  updatedAt: string
  tags: string[]
  color?: string
  source?: string
}

export interface NotePanelPosition {
  x: number
  y: number
}

export interface NotePanelSize {
  width: number
  height: number
}

export type ExportFormat = 'json' | 'markdown' | 'text'

export interface ExportOptions {
  format: ExportFormat
  includeTimestamps: boolean
  includeTags: boolean
  includeSource: boolean
}
