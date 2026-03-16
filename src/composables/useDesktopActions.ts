import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDesktopStore } from '@/stores/desktop-store'
import { apiService } from '@/services/api'
import type { DesktopItem, DesktopPosition, ContextMenuTarget, SelectionBox } from '@/types/desktop'
import type { DownloadTask } from '@/services/download'
import { DESKTOP_CONFIG } from '@/config/desktop-config'

export function useDesktopActions(tasks: () => DownloadTask[]) {
  const store = useDesktopStore()

  const isDragging = ref(false)
  const draggedItemId = ref<string | null>(null)
  const dragOffset = ref({ x: 0, y: 0 })
  const dragStartPosition = ref({ x: 0, y: 0 })

  const isSelecting = ref(false)
  const selectionBox = ref<SelectionBox | null>(null)
  const selectionStartPos = ref({ x: 0, y: 0 })

  const hoveredItemId = ref<string | null>(null)
  const tooltipPosition = ref({ x: 0, y: 0 })

  const contextMenuPosition = ref({ x: 0, y: 0 })
  const contextMenuTarget = ref<ContextMenuTarget>({ type: 'desktop' })
  const contextMenuVisible = ref(false)
  const savedSelectedIds = ref<string[]>([])

  const savedSelectedItems = computed(() => {
    return savedSelectedIds.value
      .map(id => store.getItemById(id))
      .filter((item): item is DesktopItem => item !== undefined)
  })

  const showCreateFolderDialog = ref(false)
  const renamingItemId = ref<string | null>(null)

  const desktopRef = ref<HTMLElement | null>(null)

  const hoveredItem = computed(() => {
    if (!hoveredItemId.value) return null
    return store.getItemById(hoveredItemId.value)
  })

  const currentFolder = computed(() => {
    if (!store.currentFolderId) return null
    return store.getItemById(store.currentFolderId)
  })

  const breadcrumb = computed(() => {
    const path: DesktopItem[] = []
    let folderId = store.currentFolderId
    
    while (folderId) {
      const folder = store.getItemById(folderId)
      if (folder) {
        path.unshift(folder)
        folderId = folder.folderId
      } else {
        break
      }
    }
    
    return path
  })

  function initialize() {
    store.initializeFromTasks(tasks())
  }

  function getTaskForItem(item: DesktopItem): DownloadTask | undefined {
    if (item.type !== 'file' || !item.taskId) return undefined
    return tasks().find(t => t.id === item.taskId)
  }

  function onItemMouseDown(item: DesktopItem, event: MouseEvent) {
    if (event.button !== 0) return
    
    const isMultiSelect = event.ctrlKey || event.metaKey
    
    if (!store.selectedIds.includes(item.id)) {
      store.selectItem(item.id, isMultiSelect)
    }
    
    if (item.type === 'folder' && event.detail === 2) {
      return
    }
    
    isDragging.value = true
    draggedItemId.value = item.id
    
    const rect = desktopRef.value?.getBoundingClientRect()
    if (rect) {
      dragOffset.value = {
        x: event.clientX - rect.left - item.position.x,
        y: event.clientY - rect.top - item.position.y,
      }
      dragStartPosition.value = { ...item.position }
    }
  }

  function onItemDoubleClick(item: DesktopItem) {
    if (item.type === 'folder') {
      store.openFolder(item.id)
    } else if (item.type === 'file' && item.taskId) {
      apiService.openDownloadFile(item.taskId)
    }
  }

  function onItemMouseEnter(item: DesktopItem, _event: MouseEvent) {
    hoveredItemId.value = item.id
    updateTooltipPosition(item)
  }

  function onItemMouseLeave() {
    hoveredItemId.value = null
  }

  function updateTooltipPosition(item: DesktopItem) {
    const rect = desktopRef.value?.getBoundingClientRect()
    if (rect) {
      const tooltipWidth = DESKTOP_CONFIG.TOOLTIP_WIDTH
      const tooltipHeight = DESKTOP_CONFIG.TOOLTIP_HEIGHT
      const iconWidth = DESKTOP_CONFIG.ICON_SIZE
      const iconHeight = DESKTOP_CONFIG.ICON_SIZE
      const gap = DESKTOP_CONFIG.TOOLTIP_GAP
      const borderSize = DESKTOP_CONFIG.BORDER_SIZE
      
      const iconX = item.position.x
      const iconY = item.position.y
      const contentWidth = rect.width - borderSize * 2
      const contentHeight = rect.height - borderSize * 2
      
      let x: number
      let y: number
      
      if (iconX + iconWidth + gap + tooltipWidth <= contentWidth) {
        x = iconX + iconWidth + gap
      } else {
        x = iconX - tooltipWidth - gap
      }
      
      if (iconY + tooltipHeight <= contentHeight) {
        y = iconY
      } else {
        y = contentHeight - tooltipHeight
      }
      
      x = Math.max(borderSize, Math.min(x, contentWidth - tooltipWidth))
      y = Math.max(borderSize, Math.min(y, contentHeight - tooltipHeight))
      
      tooltipPosition.value = { x, y }
    }
  }

  function onDesktopMouseDown(event: MouseEvent) {
    if (event.button === 2) return
    
    const target = event.target as HTMLElement
    if (target.closest('.desktop-icon')) return
    if (target.closest('.context-menu')) return
    
    store.clearSelection()
    
    const rect = desktopRef.value?.getBoundingClientRect()
    if (rect) {
      isSelecting.value = true
      selectionStartPos.value = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      }
      selectionBox.value = {
        startX: selectionStartPos.value.x,
        startY: selectionStartPos.value.y,
        endX: selectionStartPos.value.x,
        endY: selectionStartPos.value.y,
      }
    }
  }

  function onDesktopMouseMove(event: MouseEvent) {
    if (isDragging.value && draggedItemId.value) {
      const rect = desktopRef.value?.getBoundingClientRect()
      if (rect) {
        const grid = store.gridSize
        const borderSize = store.showGrid ? 2 : 0
        const contentWidth = rect.width - borderSize * 2
        const contentHeight = rect.height - borderSize * 2
        const newX = event.clientX - rect.left - borderSize - dragOffset.value.x
        const newY = event.clientY - rect.top - borderSize - dragOffset.value.y
        
        const maxX = contentWidth - grid
        const maxY = contentHeight - grid
        
        const boundedX = Math.max(0, Math.min(newX, maxX))
        const boundedY = Math.max(0, Math.min(newY, maxY))
        
        const draggedItem = store.getItemById(draggedItemId.value)
        if (draggedItem) {
          const deltaX = boundedX - draggedItem.position.x
          const deltaY = boundedY - draggedItem.position.y
          
          const idsToMove = store.selectedIds.length > 0 && store.selectedIds.includes(draggedItemId.value)
            ? [...store.selectedIds]
            : [draggedItemId.value]
          
          for (const id of idsToMove) {
            const itemToMove = store.getItemById(id)
            if (itemToMove) {
              const itemNewX = Math.max(0, Math.min(itemToMove.position.x + deltaX, maxX))
              const itemNewY = Math.max(0, Math.min(itemToMove.position.y + deltaY, maxY))
              store.updateItemPosition(id, { x: itemNewX, y: itemNewY })
            }
          }
        }
      }
    }
    
    if (isSelecting.value && selectionBox.value) {
      const rect = desktopRef.value?.getBoundingClientRect()
      if (rect) {
        const currentX = event.clientX - rect.left
        const currentY = event.clientY - rect.top
        
        selectionBox.value = {
          ...selectionBox.value,
          endX: currentX,
          endY: currentY,
        }
        
        updateSelectionFromBox()
      }
    }
  }

  function onDesktopMouseUp(event: MouseEvent) {
    if (isDragging.value && draggedItemId.value) {
      const item = store.getItemById(draggedItemId.value)
      if (item) {
        const grid = store.gridSize
        let snappedX = Math.round(item.position.x / grid) * grid
        let snappedY = Math.round(item.position.y / grid) * grid
        
        const occupiedPositions = new Set<string>()
        for (const otherItem of store.rootItems) {
          if (!store.selectedIds.includes(otherItem.id)) {
            occupiedPositions.add(`${otherItem.position.x},${otherItem.position.y}`)
          }
        }
        
        if (occupiedPositions.has(`${snappedX},${snappedY}`)) {
          const found = store.findNextPosition({ x: snappedX, y: snappedY })
          snappedX = found.x
          snappedY = found.y
        }
        
        const deltaX = snappedX - item.position.x
        const deltaY = snappedY - item.position.y
        
        const idsToMove = store.selectedIds.length > 0 && store.selectedIds.includes(draggedItemId.value)
          ? [...store.selectedIds]
          : [draggedItemId.value]
        
        for (const id of idsToMove) {
          const itemToMove = store.getItemById(id)
          if (itemToMove) {
            let newX = Math.round((itemToMove.position.x + deltaX) / grid) * grid
            let newY = Math.round((itemToMove.position.y + deltaY) / grid) * grid
            
            while (occupiedPositions.has(`${newX},${newY}`)) {
              newX += grid
              if (newX >= 1000) {
                newX = 0
                newY += grid
              }
            }
            
            store.updateItemPosition(id, { x: newX, y: newY })
            occupiedPositions.add(`${newX},${newY}`)
          }
        }
        
        checkDropOnFolder(item, event)
      }
    }
    
    isDragging.value = false
    draggedItemId.value = null
    isSelecting.value = false
    selectionBox.value = null
  }

  function onItemDragEnd() {
    isDragging.value = false
    draggedItemId.value = null
  }

  function updateSelectionFromBox() {
    if (!selectionBox.value) return
    
    const minX = Math.min(selectionBox.value.startX, selectionBox.value.endX)
    const maxX = Math.max(selectionBox.value.startX, selectionBox.value.endX)
    const minY = Math.min(selectionBox.value.startY, selectionBox.value.endY)
    const maxY = Math.max(selectionBox.value.startY, selectionBox.value.endY)
    
    const selectedIds: string[] = []
    
    for (const item of store.rootItems) {
      const itemCenterX = item.position.x + DESKTOP_CONFIG.ICON_CENTER_OFFSET
      const itemCenterY = item.position.y + DESKTOP_CONFIG.ICON_CENTER_OFFSET
      
      if (itemCenterX >= minX && itemCenterX <= maxX &&
          itemCenterY >= minY && itemCenterY <= maxY) {
        selectedIds.push(item.id)
      }
    }
    
    store.selectItems(selectedIds)
  }

  function checkDropOnFolder(item: DesktopItem, event: MouseEvent) {
    const rect = desktopRef.value?.getBoundingClientRect()
    if (!rect) return
    
    const dropX = event.clientX - rect.left
    const dropY = event.clientY - rect.top
    
    for (const folder of store.rootItems) {
      if (folder.type !== 'folder' || folder.id === item.id) continue
      
      const folderCenterX = folder.position.x + DESKTOP_CONFIG.ICON_CENTER_OFFSET
      const folderCenterY = folder.position.y + DESKTOP_CONFIG.ICON_CENTER_OFFSET
      const distance = Math.sqrt(
        Math.pow(dropX - folderCenterX, 2) + Math.pow(dropY - folderCenterY, 2)
      )
      
      if (distance < DESKTOP_CONFIG.DROP_DISTANCE_THRESHOLD) {
        const idsToMove = store.selectedIds.length > 0 ? [...store.selectedIds] : [item.id]
        for (const id of idsToMove) {
          const itemToMove = store.getItemById(id)
          if (itemToMove && itemToMove.folderId !== folder.id && itemToMove.id !== folder.id) {
            store.moveItemToFolder(id, folder.id)
          }
        }
        return
      }
    }
  }

  function onContextMenu(event: MouseEvent, item?: DesktopItem) {
    event.preventDefault()
    
    savedSelectedIds.value = [...store.selectedIds]
    
    if (item && !store.selectedIds.includes(item.id)) {
      store.selectItem(item.id, false)
      savedSelectedIds.value = [item.id]
    }
    
    const rect = desktopRef.value?.getBoundingClientRect()
    if (rect) {
      contextMenuPosition.value = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      }
    }
    
    contextMenuTarget.value = item
      ? { type: item.type, item }
      : { type: 'desktop' }
    contextMenuVisible.value = true
  }

  function closeContextMenu() {
    contextMenuVisible.value = false
  }

  function createFolder(name: string) {
    const rect = desktopRef.value?.getBoundingClientRect()
    let position: DesktopPosition | undefined
    
    if (rect && contextMenuTarget.value.type === 'desktop') {
      const grid = store.gridSize
      const snappedX = Math.round(contextMenuPosition.value.x / grid) * grid
      const snappedY = Math.round(contextMenuPosition.value.y / grid) * grid
      
      const occupiedPositions = new Set(
        store.rootItems.map(item => `${item.position.x},${item.position.y}`)
      )
      
      if (occupiedPositions.has(`${snappedX},${snappedY}`)) {
        position = store.findNextPosition({ x: snappedX, y: snappedY })
      } else {
        position = { x: snappedX, y: snappedY }
      }
    }
    
    store.createFolder(name, position)
    showCreateFolderDialog.value = false
    closeContextMenu()
  }

  function deleteSelectedItems() {
    const ids = savedSelectedIds.value.length > 0 ? savedSelectedIds.value : store.selectedIds
    for (const id of [...ids]) {
      store.deleteItem(id)
    }
    closeContextMenu()
  }

  function openSelectedItems() {
    const selectedIds = store.selectedIds.length > 0 ? store.selectedIds : savedSelectedIds.value
    
    for (const id of selectedIds) {
      const item = store.getItemById(id)
      if (item) {
        if (item.type === 'folder') {
          store.openFolder(item.id)
          return
        } else if (item.type === 'file' && item.taskId) {
          apiService.openDownloadFile(item.taskId)
        }
      }
    }
    closeContextMenu()
  }

  function cutSelectedItems() {
    let ids: string[] = []
    
    if (contextMenuTarget.value.item) {
      const clickedId = contextMenuTarget.value.item.id
      if (savedSelectedIds.value.includes(clickedId) || store.selectedIds.includes(clickedId)) {
        ids = savedSelectedIds.value.length > 0 ? savedSelectedIds.value : store.selectedIds
      } else {
        ids = [clickedId]
      }
    } else if (savedSelectedIds.value.length > 0) {
      ids = savedSelectedIds.value
    } else if (store.selectedIds.length > 0) {
      ids = store.selectedIds
    }
    
    if (ids.length > 0) {
      store.cutItems(ids)
    }
    closeContextMenu()
  }

  function pasteItems() {
    store.pasteItems(store.currentFolderId)
    closeContextMenu()
  }

  function startRename() {
    if (contextMenuTarget.value.item) {
      renamingItemId.value = contextMenuTarget.value.item.id
    } else if (savedSelectedIds.value.length === 1) {
      renamingItemId.value = savedSelectedIds.value[0]
    } else if (store.selectedIds.length === 1) {
      renamingItemId.value = store.selectedIds[0]
    }
    closeContextMenu()
  }

  function finishRename(newName: string) {
    if (renamingItemId.value) {
      store.renameItem(renamingItemId.value, newName)
    }
    renamingItemId.value = null
  }

  function cancelRename() {
    renamingItemId.value = null
  }

  function openFolder(folderId: string) {
    store.openFolder(folderId)
  }

  function goToRoot() {
    store.goToRoot()
  }

  function goToParent() {
    store.goToParent()
  }

  function autoArrange() {
    const rect = desktopRef.value?.getBoundingClientRect()
    if (rect) {
      const borderSize = store.showGrid ? 2 : 0
      const maxWidth = rect.width - borderSize * 2
      store.autoArrange(maxWidth)
    } else {
      store.autoArrange()
    }
    closeContextMenu()
  }

  function toggleGrid() {
    store.toggleGrid()
  }

  function exportLayout() {
    const data = {
      items: store.items,
      gridSize: store.gridSize,
      exportedAt: new Date().toISOString(),
      version: '1.0'
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `xivmind-desktop-layout-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  function importLayout(data: { items: unknown[]; gridSize?: number }) {
    if (data.items && Array.isArray(data.items)) {
      store.items = data.items as DesktopItem[]
      if (data.gridSize) {
        store.gridSize = data.gridSize
      }
    }
  }

  function handleGlobalClick(event: MouseEvent) {
    const target = event.target as HTMLElement
    if (!target.closest('.context-menu') && contextMenuVisible.value) {
      closeContextMenu()
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Delete' && store.selectedIds.length > 0) {
      store.deleteSelectedItems()
    }
    
    if (event.key === 'Escape') {
      if (contextMenuVisible.value) {
        closeContextMenu()
      }
      if (renamingItemId.value) {
        cancelRename()
      }
      store.clearSelection()
    }
    
    if (event.key === 'F2' && store.selectedIds.length === 1) {
      renamingItemId.value = store.selectedIds[0]
    }
  }

  onMounted(() => {
    document.addEventListener('click', handleGlobalClick)
    document.addEventListener('keydown', handleKeydown)
    initialize()
  })

  onUnmounted(() => {
    document.removeEventListener('click', handleGlobalClick)
    document.removeEventListener('keydown', handleKeydown)
  })

  return {
    desktopRef,
    store,
    isDragging,
    draggedItemId,
    isSelecting,
    selectionBox,
    hoveredItem,
    hoveredItemId,
    tooltipPosition,
    contextMenuVisible,
    contextMenuPosition,
    contextMenuTarget,
    savedSelectedIds,
    savedSelectedItems,
    showCreateFolderDialog,
    renamingItemId,
    currentFolder,
    breadcrumb,
    
    initialize,
    getTaskForItem,
    onItemMouseDown,
    onItemDoubleClick,
    onItemMouseEnter,
    onItemMouseLeave,
    onDesktopMouseDown,
    onDesktopMouseMove,
    onDesktopMouseUp,
    onContextMenu,
    closeContextMenu,
    createFolder,
    deleteSelectedItems,
    openSelectedItems,
    cutSelectedItems,
    pasteItems,
    startRename,
    finishRename,
    cancelRename,
    openFolder,
    goToRoot,
    goToParent,
    autoArrange,
    toggleGrid,
    exportLayout,
    importLayout,
    onItemDragEnd,
  }
}
