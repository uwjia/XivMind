import { ref, onMounted, onUnmounted, type Ref } from 'vue'
import type { NotePanelPosition, NotePanelSize } from '@/types/note'

interface UseDraggableOptions {
  initialPosition: NotePanelPosition
  onPositionChange?: (position: NotePanelPosition) => void
  boundaryPadding?: number
}

export function useDraggable(options: UseDraggableOptions) {
  const { initialPosition, onPositionChange, boundaryPadding = 10 } = options

  const position = ref<NotePanelPosition>({ ...initialPosition })
  const isDragging = ref(false)
  const dragStart = ref({ x: 0, y: 0 })

  const handleMouseDown = (e: MouseEvent) => {
    if ((e.target as HTMLElement).closest('button, input, textarea')) {
      return
    }

    isDragging.value = true
    dragStart.value = {
      x: e.clientX - position.value.x,
      y: e.clientY - position.value.y
    }

    e.preventDefault()
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging.value) return

    let newX = e.clientX - dragStart.value.x
    let newY = e.clientY - dragStart.value.y

    newX = Math.max(boundaryPadding, Math.min(newX, window.innerWidth - boundaryPadding))
    newY = Math.max(boundaryPadding, Math.min(newY, window.innerHeight - boundaryPadding))

    position.value = { x: newX, y: newY }
    onPositionChange?.({ x: newX, y: newY })
  }

  const handleMouseUp = () => {
    isDragging.value = false
  }

  onMounted(() => {
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  })

  onUnmounted(() => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  })

  return {
    position,
    isDragging,
    handleMouseDown
  }
}

interface UseResizableOptions {
  initialSize: NotePanelSize
  minSize?: NotePanelSize
  maxSize?: NotePanelSize
  onSizeChange?: (size: NotePanelSize) => void
}

export function useResizable(options: UseResizableOptions) {
  const {
    initialSize,
    minSize = { width: 280, height: 200 },
    maxSize = { width: 600, height: 800 },
    onSizeChange
  } = options

  const size = ref<NotePanelSize>({ ...initialSize })
  const isResizing = ref(false)
  const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0 })

  const handleResizeMouseDown = (e: MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    isResizing.value = true
    resizeStart.value = {
      x: e.clientX,
      y: e.clientY,
      width: size.value.width,
      height: size.value.height
    }
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing.value) return

    const deltaX = e.clientX - resizeStart.value.x
    const deltaY = e.clientY - resizeStart.value.y

    const newWidth = Math.max(
      minSize.width,
      Math.min(maxSize.width, resizeStart.value.width + deltaX)
    )
    const newHeight = Math.max(
      minSize.height,
      Math.min(maxSize.height, resizeStart.value.height + deltaY)
    )

    size.value = { width: newWidth, height: newHeight }
    onSizeChange?.({ width: newWidth, height: newHeight })
  }

  const handleMouseUp = () => {
    isResizing.value = false
  }

  onMounted(() => {
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  })

  onUnmounted(() => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  })

  return {
    size,
    isResizing,
    handleResizeMouseDown
  }
}

interface UseNotePanelKeyboardOptions {
  isVisible: Ref<boolean>
  isEditing: Ref<boolean>
  onCancelEdit: () => void
  onClearSelection: () => void
  hasSelection: Ref<boolean> | (() => boolean)
  onTogglePanel: () => void
}

export function useNotePanelKeyboard(options: UseNotePanelKeyboardOptions) {
  const {
    isVisible,
    isEditing,
    onCancelEdit,
    onClearSelection,
    hasSelection,
    onTogglePanel
  } = options

  const handleKeydown = (e: KeyboardEvent) => {
    if (!isVisible.value) return

    const getHasSelection = typeof hasSelection === 'function'
      ? hasSelection
      : () => hasSelection.value

    if (e.key === 'Escape') {
      if (isEditing.value) {
        onCancelEdit()
      } else if (getHasSelection()) {
        onClearSelection()
      }
    }

    if (e.ctrlKey && e.shiftKey && e.key === 'N') {
      e.preventDefault()
      onTogglePanel()
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })

  return {
    handleKeydown
  }
}

interface UseNotePanelResizeOptions {
  position: Ref<NotePanelPosition>
  size: Ref<NotePanelSize>
  onPositionChange: (x: number, y: number) => void
  onResetPosition: () => void
  hasUserMovedPanel: Ref<boolean> | (() => boolean)
  isVisible: Ref<boolean>
}

export function useNotePanelResize(options: UseNotePanelResizeOptions) {
  const {
    position,
    size,
    onPositionChange,
    onResetPosition,
    hasUserMovedPanel,
    isVisible
  } = options

  const adjustPositionOnResize = () => {
    const panelWidth = size.value.width
    const panelHeight = size.value.height
    const padding = 10

    let newX = position.value.x
    let newY = position.value.y

    if (position.value.x + panelWidth > window.innerWidth - padding) {
      newX = Math.max(padding, window.innerWidth - panelWidth - padding)
    }

    if (position.value.y + panelHeight > window.innerHeight - padding) {
      newY = Math.max(padding, window.innerHeight - panelHeight - padding)
    }

    if (newX !== position.value.x || newY !== position.value.y) {
      position.value = { x: newX, y: newY }
      onPositionChange(newX, newY)
    }
  }

  const handleWindowResize = () => {
    adjustPositionOnResize()

    const getHasUserMovedPanel = typeof hasUserMovedPanel === 'function'
      ? hasUserMovedPanel
      : () => hasUserMovedPanel.value

    if (!getHasUserMovedPanel() && isVisible.value) {
      onResetPosition()
      position.value = { ...position.value }
    }
  }

  onMounted(() => {
    window.addEventListener('resize', handleWindowResize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', handleWindowResize)
  })

  return {
    adjustPositionOnResize,
    handleWindowResize
  }
}
