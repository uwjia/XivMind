import { ref, onMounted, onUnmounted, type Ref } from 'vue'
import type { PdfAnnotation, AnnotationPosition, AnnotationType, HighlightColor } from '@/types/pdf'
import { DRAWING_COLORS } from '@/types/pdf'

export interface AnnotationLayerEmit {
  (e: 'annotation-create', data: { type: AnnotationType; position: AnnotationPosition; path?: { x: number; y: number }[]; color?: string; stroke_width?: number }): void
  (e: 'text-select', data: { text: string; position: AnnotationPosition; clientX: number; clientY: number }): void
  (e: 'annotation-select', annotation: PdfAnnotation | null): void
  (e: 'annotation-delete', id: string): void
  (e: 'annotation-update', data: { id: string; content: string }): void
}

export function usePdfAnnotationLayer(
  layerRef: Ref<HTMLDivElement | null>,
  props: {
    pageNumber: number
    zoom: number
    currentTool: AnnotationType | 'select' | null
    currentColor: HighlightColor
    strokeWidth: number
  },
  emit: AnnotationLayerEmit
) {
  const selectedId = ref<string | null>(null)
  const isDrawing = ref(false)
  const drawingPath = ref<{ x: number; y: number }[]>([])
  const drawingColor = ref('#FF0000')
  const showDeleteConfirm = ref(false)
  const annotationToDelete = ref<PdfAnnotation | null>(null)
  const tooltipVisible = ref(false)
  const tooltipAnnotation = ref<PdfAnnotation | null>(null)
  const tooltipStyle = ref<Record<string, string>>({})
  const showEditDialog = ref(false)
  const editContent = ref('')
  const editingAnnotation = ref<PdfAnnotation | null>(null)
  let hideTooltipTimer: ReturnType<typeof setTimeout> | null = null

  function getAnnotationStyle(annotation: PdfAnnotation) {
    const pos = annotation.position
    const style: Record<string, string> = {}
    
    if (annotation.type === 'comment') {
      const commentSize = 24 * props.zoom
      const leftOffset = -(commentSize + 8)
      style.left = `${leftOffset}px`
      style.top = `${pos.y * props.zoom}px`
      style.width = `${commentSize}px`
      style.height = `${commentSize}px`
    } else if (annotation.type === 'drawing') {
      style.left = `${pos.x * props.zoom}px`
      style.top = `${pos.y * props.zoom}px`
      style.width = `${pos.width * props.zoom}px`
      style.height = `${pos.height * props.zoom}px`
    } else {
      style.left = `${pos.x * props.zoom}px`
      style.top = `${pos.y * props.zoom}px`
      style.width = `${pos.width * props.zoom}px`
      style.height = `${pos.height * props.zoom}px`
      style.backgroundColor = annotation.color
    }
    
    if (annotation.type === 'underline') {
      style.borderBottomColor = annotation.color
    }
    
    return style
  }

  function getDrawingPath(annotation: PdfAnnotation): string {
    if (annotation.type !== 'drawing' || !annotation.content) return ''
    
    try {
      const path: { x: number; y: number }[] = JSON.parse(annotation.content)
      if (!Array.isArray(path) || path.length === 0) return ''
      
      const pos = annotation.position
      return path.reduce((d, point, i) => {
        const normalizedX = ((point.x - pos.x) / pos.width) * 100
        const normalizedY = ((point.y - pos.y) / pos.height) * 100
        return d + (i === 0 ? `M ${normalizedX} ${normalizedY}` : ` L ${normalizedX} ${normalizedY}`)
      }, '')
    } catch {
      return ''
    }
  }

  function getAnnotationStrokeWidth(annotation: PdfAnnotation): number {
    return annotation.stroke_width || 2
  }

  function selectAnnotation(annotation: PdfAnnotation) {
    selectedId.value = annotation.id
    emit('annotation-select', annotation)
  }

  function handleMouseDown(event: MouseEvent) {
    if (props.currentTool === 'select') return
    if (!layerRef.value) return

    const rect = layerRef.value.getBoundingClientRect()
    const x = (event.clientX - rect.left) / props.zoom
    const y = (event.clientY - rect.top) / props.zoom

    if (props.currentTool === 'drawing') {
      isDrawing.value = true
      drawingColor.value = DRAWING_COLORS[props.currentColor] || '#FF0000'
      drawingPath.value = [{ x, y }]
      event.preventDefault()
    }
  }

  function handleMouseMove(event: MouseEvent) {
    if (!isDrawing.value || !layerRef.value) return

    const rect = layerRef.value.getBoundingClientRect()
    const x = (event.clientX - rect.left) / props.zoom
    const y = (event.clientY - rect.top) / props.zoom

    drawingPath.value.push({ x, y })
  }

  function handleMouseUp() {
    if (isDrawing.value && drawingPath.value.length > 1) {
      const minX = Math.min(...drawingPath.value.map(p => p.x))
      const maxX = Math.max(...drawingPath.value.map(p => p.x))
      const minY = Math.min(...drawingPath.value.map(p => p.y))
      const maxY = Math.max(...drawingPath.value.map(p => p.y))

      const position: AnnotationPosition = {
        x: minX,
        y: minY,
        width: maxX - minX || 10,
        height: maxY - minY || 10,
      }

      emit('annotation-create', {
        type: 'drawing',
        position,
        path: [...drawingPath.value],
        color: drawingColor.value,
        stroke_width: props.strokeWidth,
      })
    }

    isDrawing.value = false
    drawingPath.value = []
  }

  function getPathD(path: { x: number; y: number }[]): string {
    if (path.length === 0) return ''
    
    return path.reduce((d, point, i) => {
      const scaledX = point.x * props.zoom
      const scaledY = point.y * props.zoom
      return d + (i === 0 ? `M ${scaledX} ${scaledY}` : ` L ${scaledX} ${scaledY}`)
    }, '')
  }

  function showContextMenu(_event: MouseEvent, annotation: PdfAnnotation) {
    selectedId.value = annotation.id
    annotationToDelete.value = annotation
    showDeleteConfirm.value = true
  }

  function confirmDelete() {
    if (annotationToDelete.value) {
      emit('annotation-delete', annotationToDelete.value.id)
    }
    showDeleteConfirm.value = false
    annotationToDelete.value = null
  }

  function cancelDelete() {
    showDeleteConfirm.value = false
    annotationToDelete.value = null
  }

  function showTooltip(event: MouseEvent, annotation: PdfAnnotation) {
    if (annotation.type !== 'comment') return
    
    if (hideTooltipTimer) {
      clearTimeout(hideTooltipTimer)
      hideTooltipTimer = null
    }
    
    tooltipAnnotation.value = annotation
    tooltipVisible.value = true
    
    const rect = (event.target as HTMLElement).getBoundingClientRect()
    tooltipStyle.value = {
      left: `${rect.left}px`,
      top: `${rect.bottom + 8}px`,
    }
  }

  function scheduleHideTooltip() {
    hideTooltipTimer = setTimeout(() => {
      tooltipVisible.value = false
      tooltipAnnotation.value = null
    }, 100)
  }

  function cancelHideTooltip() {
    if (hideTooltipTimer) {
      clearTimeout(hideTooltipTimer)
      hideTooltipTimer = null
    }
  }

  function hideTooltip() {
    tooltipVisible.value = false
    tooltipAnnotation.value = null
  }

  function formatDate(dateStr: string): string {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  function startEditComment() {
    if (!tooltipAnnotation.value) return
    editingAnnotation.value = tooltipAnnotation.value
    editContent.value = tooltipAnnotation.value.content || ''
    showEditDialog.value = true
    hideTooltip()
  }

  function cancelEdit() {
    showEditDialog.value = false
    editContent.value = ''
    editingAnnotation.value = null
  }

  function saveEdit() {
    if (!editingAnnotation.value) return
    emit('annotation-update', {
      id: editingAnnotation.value.id,
      content: editContent.value,
    })
    showEditDialog.value = false
    editContent.value = ''
    editingAnnotation.value = null
  }

  function deleteFromTooltip() {
    if (!tooltipAnnotation.value) return
    annotationToDelete.value = tooltipAnnotation.value
    showDeleteConfirm.value = true
    hideTooltip()
  }

  function handleTextSelection(event: MouseEvent) {
    if (!layerRef.value) return

    const pageContainer = layerRef.value.closest('.page-container')
    if (!pageContainer) return

    const target = event.target as Node
    if (!pageContainer.contains(target)) return

    const selection = window.getSelection()
    if (!selection || selection.isCollapsed) return

    const text = selection.toString()
    if (!text) return

    const range = selection.getRangeAt(0)
    const rect = range.getBoundingClientRect()
    const layerRect = layerRef.value.getBoundingClientRect()

    const position: AnnotationPosition = {
      x: (rect.left - layerRect.left) / props.zoom,
      y: (rect.top - layerRect.top) / props.zoom,
      width: rect.width / props.zoom,
      height: rect.height / props.zoom,
    }

    emit('text-select', {
      text,
      position,
      clientX: rect.right,
      clientY: rect.top,
    })
  }

  onMounted(() => {
    document.addEventListener('mouseup', handleTextSelection)
  })

  onUnmounted(() => {
    document.removeEventListener('mouseup', handleTextSelection)
    if (hideTooltipTimer) {
      clearTimeout(hideTooltipTimer)
    }
  })

  return {
    selectedId,
    isDrawing,
    drawingPath,
    drawingColor,
    showDeleteConfirm,
    annotationToDelete,
    tooltipVisible,
    tooltipAnnotation,
    tooltipStyle,
    showEditDialog,
    editContent,
    editingAnnotation,
    getAnnotationStyle,
    getDrawingPath,
    getAnnotationStrokeWidth,
    selectAnnotation,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
    getPathD,
    showContextMenu,
    confirmDelete,
    cancelDelete,
    showTooltip,
    scheduleHideTooltip,
    cancelHideTooltip,
    hideTooltip,
    formatDate,
    startEditComment,
    cancelEdit,
    saveEdit,
    deleteFromTooltip,
  }
}
