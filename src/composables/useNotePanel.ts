import { ref, onMounted, onUnmounted } from 'vue'
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
