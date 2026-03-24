<template>
  <div class="pdf-reader">
    <PdfToolbar
      :zoom="zoom"
      :zoom-percentage="zoomPercentage"
      :view-mode="viewMode"
      :current-page="currentPage"
      :total-pages="totalPages"
      :loading="loading"
      :can-go-prev="canGoPrev"
      :can-go-next="canGoNext"
      :current-tool="currentTool"
      :current-color="currentColor"
      :stroke-width="strokeWidth"
      :show-sidebar="showSidebar"
      @zoom-in="zoomIn"
      @zoom-out="zoomOut"
      @fit-width="fitToWidth"
      @fit-page="fitToPage"
      @set-zoom="setZoom"
      @toggle-view="toggleViewMode"
      @prev-page="goToPrevPage"
      @next-page="goToNextPage"
      @go-to-page="goToPage"
      @set-tool="setTool"
      @set-color="setColor"
      @set-stroke-width="setStrokeWidth"
      @toggle-sidebar="toggleSidebar"
      @close="closeReader"
    />

    <div class="pdf-content">
      <PdfSidebar
        v-if="showSidebar"
        :outline="outline"
        :thumbnails="thumbnails"
        :current-page="currentPage"
        :loading="loadingThumbnails"
        @outline-click="handleOutlineClick"
        @thumbnail-click="goToPage"
        @generate-thumbnails="generateThumbnails"
      />

      <PdfViewer
        ref="pdfViewerRef"
        :pdf-doc="pdfDoc"
        :view-mode="viewMode"
        :zoom="zoom"
        :current-page="currentPage"
        :annotations="annotations"
        :current-tool="currentTool"
        :current-color="currentColor"
        :stroke-width="strokeWidth"
        :loading="loading"
        :error="error"
        :is-user-navigating="isUserNavigating"
        @page-change="handlePageChange"
        @text-select="handleTextSelect"
        @annotation-create="handleAnnotationCreate"
        @annotation-delete="handleAnnotationDelete"
        @annotation-update="handleAnnotationUpdate"
        @container-resize="handleContainerResize"
      />

      <AnnotationPopup
        v-if="shouldShowAnnotationPopup"
        :position="popupPosition"
        :selected-text="selectedText"
        :current-color="currentColor"
        @highlight="handleHighlight"
        @underline="handleUnderline"
        @strikeout="handleStrikeout"
        @comment="handleComment"
        @copy="handleCopy"
        @close="closeAnnotationPopup"
      />
    </div>

    <CommentDialog
      v-if="showCommentDialog"
      :position="commentDialogPosition"
      :initial-content="commentContent"
      @save="saveComment"
      @close="closeCommentDialog"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, onActivated, onDeactivated, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PdfToolbar from '@/components/pdf-reader/PdfToolbar.vue'
import PdfSidebar from '@/components/pdf-reader/PdfSidebar.vue'
import PdfViewer from '@/components/pdf-reader/PdfViewer.vue'
import AnnotationPopup from '@/components/pdf-reader/AnnotationPopup.vue'
import CommentDialog from '@/components/pdf-reader/CommentDialog.vue'
import { usePdfReader, usePdfZoom, usePdfNavigation, usePdfAnnotations } from '@/composables/pdf'
import { usePdfProgressStore } from '@/stores/pdf-annotation-store'
import { pdfAnnotationAPI } from '@/services/pdf-annotation'
import type { AnnotationPosition, HighlightColor, AnnotationType, PdfOutlineItem } from '@/types/pdf'

const route = useRoute()
const router = useRouter()

const paperId = computed(() => route.params.paperId as string)

const containerWidth = ref(800)
const containerHeight = ref(600)
const pageWidth = ref(612)
const pageHeight = ref(792)
const showSidebar = ref(true)
const loadingThumbnails = ref(false)

const showAnnotationPopup = ref(false)
const popupPosition = ref({ x: 0, y: 0 })
const selectedText = ref('')
const textSelectionPosition = ref<AnnotationPosition | null>(null)
const textSelectionPage = ref(1)

const showCommentDialog = ref(false)
const commentDialogPosition = ref({ x: 0, y: 0 })
const commentContent = ref('')
const commentPosition = ref<AnnotationPosition | null>(null)

const pdfViewerRef = ref<InstanceType<typeof PdfViewer> | null>(null)
const isLoadingPdf = ref(false)

const {
  pdfDoc,
  loading,
  error,
  totalPages,
  outline,
  thumbnails,
  isLoaded,
  loadPdf,
  generateThumbnails: doGenerateThumbnails,
  cleanup: cleanupPdf,
} = usePdfReader()

const {
  zoom,
  zoomPercentage,
  setZoom,
  zoomIn,
  zoomOut,
  fitToWidth,
  fitToPage,
} = usePdfZoom(containerWidth, containerHeight, pageWidth, pageHeight)

const {
  currentPage,
  viewMode,
  canGoPrev,
  canGoNext,
  isUserNavigating,
  goToPage,
  goToPrevPage,
  goToNextPage,
  toggleViewMode,
  updateCurrentPageFromScroll,
} = usePdfNavigation(totalPages)

const {
  annotations,
  currentTool,
  currentColor,
  strokeWidth,
  loadAnnotations,
  createHighlight,
  createUnderline,
  createStrikeout,
  createComment,
  createDrawing,
  deleteAnnotation,
  updateAnnotation,
  setTool,
  setColor,
  setStrokeWidth,
  clearAnnotations,
} = usePdfAnnotations(paperId)

const progressStore = usePdfProgressStore()

const shouldShowAnnotationPopup = computed(() => {
  if (!showAnnotationPopup.value || !selectedText.value) {
    return false
  }
  return currentTool.value === 'select' || currentTool.value === 'highlight' || currentTool.value === 'underline'
})

let saveProgressTimeout: ReturnType<typeof setTimeout> | null = null

function debouncedSaveProgress() {
  if (saveProgressTimeout) {
    clearTimeout(saveProgressTimeout)
  }
  saveProgressTimeout = setTimeout(() => {
    if (paperId.value && isLoaded.value) {
      progressStore.saveProgress(
        paperId.value,
        currentPage.value,
        totalPages.value,
        zoom.value,
        viewMode.value
      )
    }
  }, 500)
}

async function loadPdfFile() {
  if (!paperId.value) return
  if (isLoadingPdf.value) return
  isLoadingPdf.value = true

  cleanupPdf()
  clearAnnotations()
  thumbnails.value = []
  outline.value = []

  try {
    const savedProgress = await progressStore.loadProgress(paperId.value)
    
    if (savedProgress) {
      currentPage.value = savedProgress.page
      if (savedProgress.viewMode !== viewMode.value) {
        viewMode.value = savedProgress.viewMode
      }
    } else {
      currentPage.value = 1
    }
    
    const fileUrl = pdfAnnotationAPI.getPdfFileUrl(paperId.value)
    const success = await loadPdf(fileUrl)
    
    if (success && pdfDoc.value) {
      const firstPage = await pdfDoc.value.getPage(1)
      const viewport = firstPage.getViewport({ scale: 1 })
      pageWidth.value = viewport.width
      pageHeight.value = viewport.height
      
      await loadAnnotations()
      
      if (savedProgress) {
        setZoom(savedProgress.zoom)
      } else {
        fitToWidth()
      }
    }
  } catch (e) {
    console.error('Failed to load PDF:', e)
  } finally {
    isLoadingPdf.value = false
  }
}

function handlePageChange(page: number) {
  updateCurrentPageFromScroll(page)
}

function handleTextSelect(data: { text: string; position: AnnotationPosition; pageNumber: number; clientX: number; clientY: number }) {
  selectedText.value = data.text
  textSelectionPosition.value = data.position
  textSelectionPage.value = data.pageNumber
  popupPosition.value = { x: data.clientX, y: data.clientY }
  showAnnotationPopup.value = true
}

function handleAnnotationCreate(data: { type: AnnotationType; position: AnnotationPosition; pageNumber: number; path?: { x: number; y: number }[]; color?: string; stroke_width?: number }) {
  if (data.type === 'comment') {
    commentPosition.value = data.position
    commentDialogPosition.value = { x: popupPosition.value.x, y: popupPosition.value.y }
    showCommentDialog.value = true
  } else if (data.type === 'drawing') {
    if (data.path && data.color) {
      createDrawing(data.pageNumber, data.position, JSON.stringify(data.path), data.color, data.stroke_width)
    }
  }
}

async function handleAnnotationDelete(id: string) {
  await deleteAnnotation(id)
}

async function handleAnnotationUpdate(data: { id: string; content: string }) {
  await updateAnnotation(data.id, { content: data.content })
}

function handleContainerResize(data: { width: number; height: number }) {
  containerWidth.value = data.width
  containerHeight.value = data.height
}

async function handleHighlight(color: HighlightColor) {
  if (textSelectionPosition.value) {
    await createHighlight(textSelectionPage.value, textSelectionPosition.value, color)
    closeAnnotationPopup()
  }
}

async function handleUnderline(color: HighlightColor) {
  if (textSelectionPosition.value) {
    await createUnderline(textSelectionPage.value, textSelectionPosition.value, color)
    closeAnnotationPopup()
  }
}

async function handleStrikeout(color: HighlightColor) {
  if (textSelectionPosition.value) {
    await createStrikeout(textSelectionPage.value, textSelectionPosition.value, color)
    closeAnnotationPopup()
  }
}

function handleComment() {
  if (textSelectionPosition.value) {
    commentPosition.value = textSelectionPosition.value
    commentDialogPosition.value = { x: popupPosition.value.x + 20, y: popupPosition.value.y + 20 }
    showCommentDialog.value = true
  }
}

async function handleCopy() {
  if (selectedText.value) {
    try {
      await navigator.clipboard.writeText(selectedText.value)
    } catch (e) {
      console.error('Failed to copy text:', e)
    }
  }
  closeAnnotationPopup()
}

function closeAnnotationPopup() {
  showAnnotationPopup.value = false
  selectedText.value = ''
  textSelectionPosition.value = null
}

function closeCommentDialog() {
  showCommentDialog.value = false
  commentContent.value = ''
  commentPosition.value = null
}

async function saveComment(content: string) {
  if (commentPosition.value) {
    await createComment(textSelectionPage.value, commentPosition.value, content)
    closeCommentDialog()
    closeAnnotationPopup()
  }
}

function handleOutlineClick(item: PdfOutlineItem) {
  console.log('[PdfReader] handleOutlineClick:', JSON.stringify(item))
  if (typeof item.dest === 'number') {
    goToPage(item.dest)
    if (item.y !== null && pdfViewerRef.value) {
      console.log('[PdfReader] calling scrollToY with page:', item.dest, 'y:', item.y)
      pdfViewerRef.value.scrollToY(item.dest, item.y)
    }
  } else {
    console.log('[PdfReader] item.dest is not a number:', item.dest)
  }
}

async function generateThumbnails() {
  loadingThumbnails.value = true
  try {
    await doGenerateThumbnails(150)
  } finally {
    loadingThumbnails.value = false
  }
}

function toggleSidebar() {
  showSidebar.value = !showSidebar.value
}

function closeReader() {
  router.back()
}

function handleSelectionChange() {
  const selection = window.getSelection()
  if (!selection || selection.isCollapsed || !selection.toString().trim()) {
    selectedText.value = ''
    showAnnotationPopup.value = false
    textSelectionPosition.value = null
  }
}

watch([currentPage, zoom, viewMode], () => {
  debouncedSaveProgress()
})

watch(selectedText, (newText) => {
  if (!newText) {
    showAnnotationPopup.value = false
  }
})

watch(currentTool, (newTool) => {
  const allowedTools = ['select', 'highlight', 'underline']
  if (!allowedTools.includes(newTool || '')) {
    showAnnotationPopup.value = false
    selectedText.value = ''
    textSelectionPosition.value = null
  }
})

watch(paperId, (newPaperId) => {
  if (newPaperId) {
    loadPdfFile()
  }
}, { immediate: true })

onMounted(() => {
  document.body.style.overflow = 'hidden'
  document.addEventListener('selectionchange', handleSelectionChange)
})

onUnmounted(() => {
  document.body.style.overflow = ''
  document.removeEventListener('selectionchange', handleSelectionChange)
  if (saveProgressTimeout) {
    clearTimeout(saveProgressTimeout)
  }
  if (paperId.value && isLoaded.value) {
    progressStore.saveProgress(
      paperId.value,
      currentPage.value,
      totalPages.value,
      zoom.value,
      viewMode.value
    )
  }
})

onActivated(() => {
  document.body.style.overflow = 'hidden'
})

onDeactivated(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.pdf-reader {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background: var(--pdf-bg);
  overflow: hidden;
  z-index: 950;
}

.pdf-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}
</style>
