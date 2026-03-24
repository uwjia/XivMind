export type AnnotationType = 'highlight' | 'underline' | 'strikeout' | 'drawing' | 'comment'

export interface AnnotationPosition {
  x: number
  y: number
  width: number
  height: number
}

export interface PdfAnnotation {
  id: string
  paper_id: string
  type: AnnotationType
  page_number: number
  position: AnnotationPosition
  content?: string
  color: string
  stroke_width?: number
  created_at: string
  updated_at: string
}

export interface CreateAnnotationData {
  paper_id: string
  type: AnnotationType
  page_number: number
  position: AnnotationPosition
  content?: string
  color: string
  stroke_width?: number
}

export interface UpdateAnnotationData {
  position?: AnnotationPosition
  content?: string
  color?: string
}

export interface PdfOutlineItem {
  title: string
  dest: number | string | null
  y: number | null
  items: PdfOutlineItem[]
}

export interface PdfThumbnail {
  page_number: number
  src: string
  width: number
  height: number
}

export interface PdfReadingProgress {
  paper_id: string
  current_page: number
  total_pages: number
  zoom_level: number
  view_mode: ViewMode
  last_read_at: string
}

export type ViewMode = 'single' | 'continuous'

export interface SaveProgressData {
  current_page: number
  total_pages: number
  zoom_level: number
  view_mode: ViewMode
}

export interface TextSelection {
  page_number: number
  start_offset: number
  end_offset: number
  text: string
  bounding_rect: AnnotationPosition
}

export interface PageRenderEvent {
  page_number: number
  canvas: HTMLCanvasElement
  viewport: {
    width: number
    height: number
    scale: number
  }
}

export const HIGHLIGHT_COLORS = {
  yellow: 'rgba(255, 235, 59, 0.4)',
  green: 'rgba(76, 175, 80, 0.4)',
  blue: 'rgba(33, 150, 243, 0.4)',
  pink: 'rgba(233, 30, 99, 0.4)',
  purple: 'rgba(156, 39, 176, 0.4)',
} as const

export type HighlightColor = keyof typeof HIGHLIGHT_COLORS

export const DRAWING_COLORS: Record<HighlightColor, string> = {
  yellow: '#FFEB3B',
  green: '#4CAF50',
  blue: '#2196F3',
  pink: '#E91E63',
  purple: '#9C27B0',
} as const

export const ZOOM_LEVELS = [0.5, 0.75, 1, 1.25, 1.5, 2, 3, 4] as const

export const MIN_ZOOM = 0.25
export const MAX_ZOOM = 5
export const ZOOM_STEP = 0.25
