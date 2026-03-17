import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DesktopItem, DesktopPosition, DesktopItemType } from '@/types/desktop'
import { DESKTOP_CONFIG } from '@/config/desktop-config'

function generateId(): string {
  return `desktop-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

function snapToGrid(value: number, gridSize: number): number {
  return Math.round(value / gridSize) * gridSize
}

export const useDesktopStore = defineStore('desktop', () => {
  const items = ref<DesktopItem[]>([])
  const selectedIds = ref<string[]>([])
  const currentFolderId = ref<string | undefined>(undefined)
  const gridSize = ref<number>(DESKTOP_CONFIG.GRID_SIZE)
  const showGrid = ref(true)
  const clipboardItems = ref<DesktopItem[]>([])
  const clipboardOperation = ref<'cut' | 'copy' | null>(null)

  const rootItems = computed(() => 
    items.value.filter(item => item.folderId === currentFolderId.value)
  )

  const selectedItems = computed(() =>
    items.value.filter(item => selectedIds.value.includes(item.id))
  )

  function toggleGrid() {
    showGrid.value = !showGrid.value
  }

  function cutItems(itemIds: string[]) {
    clipboardItems.value = items.value
      .filter(item => itemIds.includes(item.id))
      .map(item => ({ ...item }))
    clipboardOperation.value = 'cut'
  }

  function copyItems(itemIds: string[]) {
    clipboardItems.value = items.value
      .filter(item => itemIds.includes(item.id))
      .map(item => ({ ...item }))
    clipboardOperation.value = 'copy'
  }

  function pasteItems(targetFolderId?: string | undefined) {
    if (clipboardItems.value.length === 0) return
    
    const grid = gridSize.value
    const newItems: DesktopItem[] = []
    
    const targetItems = items.value.filter(i => i.folderId === targetFolderId)
    const existingNames = new Set(targetItems.map(i => i.name))
    const existingPositions = new Set(
      targetItems.map(i => `${i.position.x},${i.position.y}`)
    )
    
    let currentX = 0
    let currentY = 0
    
    while (existingPositions.has(`${currentX},${currentY}`)) {
      currentX += grid
      if (currentX >= DESKTOP_CONFIG.MAX_WIDTH) {
        currentX = 0
        currentY += grid
      }
    }
    
    for (const clipItem of clipboardItems.value) {
      let newName = clipItem.name
      if (existingNames.has(newName)) {
        let counter = 1
        while (existingNames.has(`${newName} (${counter})`)) {
          counter++
        }
        newName = `${newName} (${counter})`
      }
      
      if (clipboardOperation.value === 'cut') {
        const existingIndex = items.value.findIndex(i => i.id === clipItem.id)
        if (existingIndex !== -1) {
          const updatedItem: DesktopItem = {
            ...items.value[existingIndex],
            name: newName,
            folderId: targetFolderId,
            position: { x: currentX, y: currentY },
            updatedAt: new Date().toISOString()
          }
          newItems.push(updatedItem)
        }
      } else if (clipboardOperation.value === 'copy') {
        const newItem: DesktopItem = {
          ...clipItem,
          id: generateId(),
          name: newName,
          folderId: targetFolderId,
          position: { x: currentX, y: currentY },
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        newItems.push(newItem)
      }
      
      existingNames.add(newName)
      existingPositions.add(`${currentX},${currentY}`)
      
      currentX += grid
      if (currentX >= DESKTOP_CONFIG.MAX_WIDTH) {
        currentX = 0
        currentY += grid
      }
      while (existingPositions.has(`${currentX},${currentY}`)) {
        currentX += grid
        if (currentX >= DESKTOP_CONFIG.MAX_WIDTH) {
          currentX = 0
          currentY += grid
        }
      }
    }
    
    if (clipboardOperation.value === 'cut') {
      const cutIds = new Set(clipboardItems.value.map(i => i.id))
      items.value = [
        ...items.value.filter(i => !cutIds.has(i.id)),
        ...newItems
      ]
      clipboardItems.value = []
      clipboardOperation.value = null
    } else if (clipboardOperation.value === 'copy') {
      items.value = [...items.value, ...newItems]
    }
  }

  function hasClipboardItems(): boolean {
    return clipboardItems.value.length > 0
  }

  function initializeFromTasks(tasks: Array<{ id: string; paper_id: string; arxiv_id?: string; title: string; pdf_url?: string }>) {
    items.value = []
    
    // Fix orphaned files (folderId points to non-existent folder)
    const folderIds = new Set(
      items.value.filter(i => i.type === 'folder').map(i => i.id)
    )
    for (const item of items.value) {
      if (item.folderId && !folderIds.has(item.folderId)) {
        item.folderId = undefined
      }
    }
    
    const existingTaskIds = new Set(
      items.value.filter(item => item.type === 'file').map(item => item.taskId)
    )
    
    const newItems: DesktopItem[] = []
    const grid = gridSize.value
    
    const rootLevelItems = items.value.filter(item => item.folderId === undefined)
    const existingPositions = new Set(
      rootLevelItems.map(item => `${item.position.x},${item.position.y}`)
    )
    const existingNames = new Set(
      rootLevelItems.map(item => item.name)
    )
    
    let x = 0
    let y = 0
    
    for (const task of tasks) {
      if (!existingTaskIds.has(task.id)) {
        let displayName = task.arxiv_id || task.paper_id
        
        if (task.pdf_url && !displayName.includes('v')) {
          const versionMatch = task.pdf_url.match(/v(\d+)/)
          if (versionMatch) {
            displayName = `${displayName}v${versionMatch[1]}`
          }
        }
        
        if (existingNames.has(displayName)) {
          let counter = 1
          while (existingNames.has(`${displayName} (${counter})`)) {
            counter++
          }
          displayName = `${displayName} (${counter})`
        }
        
        while (existingPositions.has(`${x},${y}`)) {
          x += grid
          if (x >= DESKTOP_CONFIG.MAX_WIDTH) {
            x = 0
            y += grid
          }
        }
        
        newItems.push({
          id: generateId(),
          type: 'file',
          position: { x, y },
          name: displayName,
          taskId: task.id,
          folderId: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        })
        
        existingPositions.add(`${x},${y}`)
        existingNames.add(displayName)
        
        x += grid
        if (x >= DESKTOP_CONFIG.MAX_WIDTH) {
          x = 0
          y += grid
        }
      }
    }
    
    if (newItems.length > 0) {
      items.value = [...items.value, ...newItems]
    }
  }

  function createFolder(name: string, position?: DesktopPosition): DesktopItem {
    let finalName = name
    const folderId = currentFolderId.value
    const existingNames = new Set(
      items.value.filter(i => i.folderId === folderId).map(i => i.name)
    )
    
    if (existingNames.has(finalName)) {
      let counter = 1
      while (existingNames.has(`${finalName} (${counter})`)) {
        counter++
      }
      finalName = `${finalName} (${counter})`
    }
    
    const pos = position || findNextPosition()
    const folder: DesktopItem = {
      id: generateId(),
      type: 'folder',
      position: pos,
      name: finalName,
      children: [],
      folderId: currentFolderId.value,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    items.value.push(folder)
    return folder
  }

  function findNextPosition(startFrom?: DesktopPosition): DesktopPosition {
    const existingPositions = new Set(
      rootItems.value.map(item => `${item.position.x},${item.position.y}`)
    )
    
    const grid = gridSize.value
    let x = startFrom ? snapToGrid(startFrom.x, grid) : 0
    let y = startFrom ? snapToGrid(startFrom.y, grid) : 0
    
    while (existingPositions.has(`${x},${y}`)) {
      x += grid
      if (x >= DESKTOP_CONFIG.MAX_WIDTH) {
        x = 0
        y += grid
      }
    }
    
    return { x, y }
  }

  function updateItemPosition(itemId: string, position: DesktopPosition) {
    const item = items.value.find(i => i.id === itemId)
    if (item) {
      item.position = {
        x: snapToGrid(position.x, gridSize.value),
        y: snapToGrid(position.y, gridSize.value),
      }
      item.updatedAt = new Date().toISOString()
    }
  }

  function selectItem(itemId: string, multiSelect: boolean = false) {
    if (multiSelect) {
      const index = selectedIds.value.indexOf(itemId)
      if (index > -1) {
        selectedIds.value.splice(index, 1)
      } else {
        selectedIds.value.push(itemId)
      }
    } else {
      selectedIds.value = [itemId]
    }
  }

  function selectItems(itemIds: string[]) {
    selectedIds.value = itemIds
  }

  function clearSelection() {
    selectedIds.value = []
  }

  function deleteItem(itemId: string) {
    const item = items.value.find(i => i.id === itemId)
    if (!item) return

    if (item.type === 'folder') {
      const childItems = items.value.filter(i => i.folderId === itemId)
      for (const childItem of childItems) {
        childItem.folderId = item.folderId
      }
    }

    if (item.folderId) {
      const parentFolder = items.value.find(i => i.id === item.folderId)
      if (parentFolder && parentFolder.children) {
        parentFolder.children = parentFolder.children.filter(id => id !== itemId)
      }
    }

    const index = items.value.findIndex(i => i.id === itemId)
    if (index > -1) {
      items.value.splice(index, 1)
    }
    
    selectedIds.value = selectedIds.value.filter(id => id !== itemId)
  }

  function deleteSelectedItems() {
    for (const id of [...selectedIds.value]) {
      deleteItem(id)
    }
  }

  function renameItem(itemId: string, newName: string) {
    const item = items.value.find(i => i.id === itemId)
    if (item) {
      const folderId = item.folderId
      const existingNames = new Set(
        items.value.filter(i => i.folderId === folderId && i.id !== itemId).map(i => i.name)
      )
      
      let finalName = newName
      if (existingNames.has(finalName)) {
        let counter = 1
        while (existingNames.has(`${finalName} (${counter})`)) {
          counter++
        }
        finalName = `${finalName} (${counter})`
      }
      
      item.name = finalName
      item.updatedAt = new Date().toISOString()
    }
  }

  function moveItemToFolder(itemId: string, folderId: string | undefined) {
    const itemIndex = items.value.findIndex(i => i.id === itemId)
    if (itemIndex === -1) return
    
    const item = items.value[itemIndex]
    
    if (item.folderId) {
      const oldFolder = items.value.find(i => i.id === item.folderId)
      if (oldFolder && oldFolder.children) {
        oldFolder.children = oldFolder.children.filter(id => id !== itemId)
      }
    }
    
    const targetItems = items.value.filter(i => i.folderId === folderId && i.id !== itemId)
    const existingPositions = new Set(
      targetItems.map(i => `${i.position.x},${i.position.y}`)
    )
    const existingNames = new Set(
      targetItems.map(i => i.name)
    )
    
    let finalName = item.name
    if (existingNames.has(finalName)) {
      let counter = 1
      while (existingNames.has(`${finalName} (${counter})`)) {
        counter++
      }
      finalName = `${finalName} (${counter})`
    }
    
    const grid = gridSize.value
    let x = 0
    let y = 0
    
    while (existingPositions.has(`${x},${y}`)) {
      x += grid
      if (x >= DESKTOP_CONFIG.MAX_WIDTH) {
        x = 0
        y += grid
      }
    }
    
    items.value[itemIndex] = {
      ...item,
      name: finalName,
      folderId: folderId,
      position: { x, y },
      updatedAt: new Date().toISOString()
    }
    
    if (folderId) {
      const newFolder = items.value.find(i => i.id === folderId)
      if (newFolder) {
        if (!newFolder.children) {
          newFolder.children = []
        }
        if (!newFolder.children.includes(itemId)) {
          newFolder.children.push(itemId)
        }
      }
    }
  }

  function openFolder(folderId: string) {
    currentFolderId.value = folderId
    selectedIds.value = []
  }

  function goToRoot() {
    currentFolderId.value = undefined
    selectedIds.value = []
  }

  function goToParent() {
    if (currentFolderId.value) {
      const currentFolder = items.value.find(i => i.id === currentFolderId.value)
      currentFolderId.value = currentFolder?.folderId
      selectedIds.value = []
    }
  }

  function autoArrange(maxWidth: number = DESKTOP_CONFIG.MAX_WIDTH) {
    const grid = gridSize.value
    
    const currentItems = items.value.filter(item => item.folderId === currentFolderId.value)
    
    const sortedItems = [...currentItems].sort((a, b) => {
      const aIsFolder = a.type === 'folder'
      const bIsFolder = b.type === 'folder'
      
      if (aIsFolder && !bIsFolder) return -1
      if (!aIsFolder && bIsFolder) return 1
      
      return a.name.localeCompare(b.name)
    })
    
    const updatedItems = items.value.map(item => {
      if (item.folderId === currentFolderId.value) {
        const sortedIndex = sortedItems.findIndex(i => i.id === item.id)
        if (sortedIndex === -1) return item
        
        const position = {
          x: (sortedIndex % Math.floor(maxWidth / grid)) * grid,
          y: Math.floor(sortedIndex / Math.floor(maxWidth / grid)) * grid
        }
        
        return {
          ...item,
          position: position as DesktopPosition,
          updatedAt: new Date().toISOString()
        }
      }
      return item
    })
    
    items.value = updatedItems
  }

  function getItemById(itemId: string): DesktopItem | undefined {
    return items.value.find(i => i.id === itemId)
  }

  function getItemsByType(type: DesktopItemType): DesktopItem[] {
    return items.value.filter(i => i.type === type)
  }

  function getFolderChildren(folderId: string): DesktopItem[] {
    return items.value.filter(i => i.folderId === folderId)
  }

  return {
    items,
    selectedIds,
    currentFolderId,
    gridSize,
    showGrid,
    rootItems,
    selectedItems,
    clipboardItems,
    clipboardOperation,
    initializeFromTasks,
    createFolder,
    findNextPosition,
    updateItemPosition,
    selectItem,
    selectItems,
    clearSelection,
    deleteItem,
    deleteSelectedItems,
    renameItem,
    moveItemToFolder,
    openFolder,
    goToRoot,
    goToParent,
    autoArrange,
    toggleGrid,
    cutItems,
    copyItems,
    pasteItems,
    hasClipboardItems,
    getItemById,
    getItemsByType,
    getFolderChildren,
  }
}, {
  persist: {
    key: 'xivmind-desktop-layout',
    paths: ['items', 'gridSize', 'showGrid', 'clipboardItems', 'clipboardOperation'],
  }
})
