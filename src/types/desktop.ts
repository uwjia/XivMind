export type DesktopItemType = 'file' | 'folder'

export interface DesktopPosition {
  x: number
  y: number
}

export interface DesktopItem {
  id: string
  type: DesktopItemType
  position: DesktopPosition
  name: string
  taskId?: string
  folderId?: string
  children?: string[]
  createdAt: string
  updatedAt: string
}

export interface DesktopLayout {
  items: DesktopItem[]
  selectedIds: string[]
  gridSize: number
  viewMode: 'list' | 'desktop'
}

export interface ContextMenuTarget {
  type: 'desktop' | 'file' | 'folder'
  item?: DesktopItem
}

export interface SelectionBox {
  startX: number
  startY: number
  endX: number
  endY: number
}
