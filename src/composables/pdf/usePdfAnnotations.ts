import { ref, computed, type Ref } from 'vue'
import { usePdfAnnotationStore } from '@/stores/pdf-annotation-store'
import type { 
  PdfAnnotation, 
  CreateAnnotationData, 
  AnnotationType, 
  AnnotationPosition,
  TextSelection,
  HighlightColor,
} from '@/types/pdf'
import { HIGHLIGHT_COLORS } from '@/types/pdf'

export function usePdfAnnotations(paperId: Ref<string>) {
  const store = usePdfAnnotationStore()
  
  const selectedAnnotation = ref<PdfAnnotation | null>(null)
  const currentColor = ref<HighlightColor>('yellow')
  const currentTool = ref<AnnotationType | 'select' | null>('select')
  const strokeWidth = ref(2)
  const textSelection = ref<TextSelection | null>(null)

  const annotations = computed(() => store.annotations)
  const loading = computed(() => store.loading)

  async function loadAnnotations() {
    if (paperId.value) {
      await store.loadAnnotations(paperId.value)
    }
  }

  async function createHighlight(
    pageNumber: number,
    position: AnnotationPosition,
    color: HighlightColor = 'yellow'
  ): Promise<PdfAnnotation | null> {
    if (!paperId.value) return null

    const data: CreateAnnotationData = {
      paper_id: paperId.value,
      type: 'highlight',
      page_number: pageNumber,
      position,
      color: HIGHLIGHT_COLORS[color],
    }

    return store.createAnnotation(data)
  }

  async function createUnderline(
    pageNumber: number,
    position: AnnotationPosition,
    color: HighlightColor = 'yellow'
  ): Promise<PdfAnnotation | null> {
    if (!paperId.value) return null

    const data: CreateAnnotationData = {
      paper_id: paperId.value,
      type: 'underline',
      page_number: pageNumber,
      position,
      color: HIGHLIGHT_COLORS[color],
    }

    return store.createAnnotation(data)
  }

  async function createStrikeout(
    pageNumber: number,
    position: AnnotationPosition,
    color: HighlightColor = 'yellow'
  ): Promise<PdfAnnotation | null> {
    if (!paperId.value) return null

    const data: CreateAnnotationData = {
      paper_id: paperId.value,
      type: 'strikeout',
      page_number: pageNumber,
      position,
      color: HIGHLIGHT_COLORS[color],
    }

    return store.createAnnotation(data)
  }

  async function createComment(
    pageNumber: number,
    position: AnnotationPosition,
    content: string
  ): Promise<PdfAnnotation | null> {
    if (!paperId.value) return null

    const data: CreateAnnotationData = {
      paper_id: paperId.value,
      type: 'comment',
      page_number: pageNumber,
      position,
      content,
      color: '#FFC107',
    }

    return store.createAnnotation(data)
  }

  async function createDrawing(
    pageNumber: number,
    position: AnnotationPosition,
    path: string,
    color: string = '#FF0000',
    stroke_width: number = 2
  ): Promise<PdfAnnotation | null> {
    if (!paperId.value) return null

    const data: CreateAnnotationData = {
      paper_id: paperId.value,
      type: 'drawing',
      page_number: pageNumber,
      position,
      content: path,
      color,
      stroke_width,
    }

    return store.createAnnotation(data)
  }

  async function updateAnnotation(
    id: string,
    data: Partial<CreateAnnotationData>
  ): Promise<boolean> {
    return store.updateAnnotation(id, data)
  }

  async function deleteAnnotation(id: string): Promise<boolean> {
    return store.deleteAnnotation(id)
  }

  function selectAnnotation(annotation: PdfAnnotation | null) {
    selectedAnnotation.value = annotation
  }

  function setTool(tool: AnnotationType | 'select' | null) {
    currentTool.value = tool
  }

  function setColor(color: HighlightColor) {
    currentColor.value = color
  }

  function setStrokeWidth(width: number) {
    console.log('[usePdfAnnotations] setStrokeWidth called:', width)
    strokeWidth.value = width
  }

  function setTextSelection(selection: TextSelection | null) {
    textSelection.value = selection
  }

  function getAnnotationsForPage(pageNumber: number): PdfAnnotation[] {
    return store.getAnnotationsForPage(pageNumber)
  }

  function clearSelection() {
    selectedAnnotation.value = null
    textSelection.value = null
  }

  function clearAnnotations() {
    store.clearAnnotations()
  }

  return {
    annotations,
    loading,
    selectedAnnotation,
    currentColor,
    currentTool,
    strokeWidth,
    textSelection,
    loadAnnotations,
    createHighlight,
    createUnderline,
    createStrikeout,
    createComment,
    createDrawing,
    updateAnnotation,
    deleteAnnotation,
    selectAnnotation,
    setTool,
    setColor,
    setStrokeWidth,
    setTextSelection,
    getAnnotationsForPage,
    clearSelection,
    clearAnnotations,
  }
}
