<template>
  <div class="pdf-viewer" ref="containerRef">
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading PDF...</p>
    </div>

    <div v-else-if="error" class="error-overlay">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10" stroke-width="2"/>
        <line x1="15" y1="9" x2="9" y2="15" stroke-width="2"/>
        <line x1="9" y1="9" x2="15" y2="15" stroke-width="2"/>
      </svg>
      <p>{{ error }}</p>
      <button @click="retryLoad">Retry</button>
    </div>

    <div 
      v-else-if="pdfDoc"
      ref="scrollContainerRef"
      class="pdf-container"
      :class="{ 'single-page': viewMode === 'single', 'continuous': viewMode === 'continuous' }"
      @scroll="handleScroll"
    >
      <div 
        v-for="pageNum in visiblePages" 
        :key="`${pageNum}`"
        class="page-container"
        :data-page="pageNum"
        :style="{ '--scale-factor': zoom }"
      >
        <canvas
          :ref="el => canvasRefs[pageNum] = el as HTMLCanvasElement"
          class="pdf-canvas"
        ></canvas>
        <div 
          :ref="el => textLayerRefs[pageNum] = el as HTMLDivElement"
          class="text-layer"
          :class="{ 'selecting': currentTool === 'select' }"
        ></div>
        <PdfAnnotationLayer
          v-if="pageRendered[pageNum]"
          :page-number="pageNum"
          :annotations="getPageAnnotations(pageNum)"
          :zoom="zoom"
          :current-tool="currentTool"
          :current-color="currentColor"
          :stroke-width="strokeWidth"
          @annotation-create="(data) => handleAnnotationCreate(data, pageNum)"
          @annotation-delete="(id) => emit('annotation-delete', id)"
          @annotation-update="(data) => emit('annotation-update', data)"
          @text-select="(data) => handleTextSelect(data, pageNum)"
        />
      </div>
    </div>

    <div v-else class="empty-overlay">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke-width="2"/>
        <polyline points="14 2 14 8 20 8" stroke-width="2"/>
      </svg>
      <p>No PDF loaded</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, onActivated, nextTick } from 'vue'
import * as pdfjsLib from 'pdfjs-dist'
import PdfAnnotationLayer from '@/components/pdf-reader/PdfAnnotationLayer.vue'
import type { 
  PdfAnnotation, 
  AnnotationPosition, 
  AnnotationType, 
  HighlightColor,
  ViewMode 
} from '@/types/pdf'

const props = defineProps<{
  pdfDoc: any
  viewMode: ViewMode
  zoom: number
  currentPage: number
  annotations: PdfAnnotation[]
  currentTool: AnnotationType | 'select' | null
  currentColor: HighlightColor
  strokeWidth: number
  loading: boolean
  error: string | null
  isUserNavigating: boolean
}>()

const emit = defineEmits<{
  'page-change': [page: number]
  'text-select': [data: { text: string; position: AnnotationPosition; pageNumber: number; clientX: number; clientY: number }]
  'annotation-create': [data: { type: AnnotationType; position: AnnotationPosition; pageNumber: number; path?: { x: number; y: number }[]; color?: string; stroke_width?: number }]
  'annotation-delete': [id: string]
  'annotation-update': [data: { id: string; content: string }]
  'container-resize': [data: { width: number; height: number }]
}>()

const containerRef = ref<HTMLDivElement | null>(null)
const scrollContainerRef = ref<HTMLDivElement | null>(null)
const canvasRefs = ref<Record<number, HTMLCanvasElement>>({})
const textLayerRefs = ref<Record<number, HTMLDivElement>>({})
const pageRendered = ref<Record<number, boolean>>({})
const renderedPages = ref<Set<number>>(new Set())
const pendingRenders = new Map<number, pdfjsLib.RenderTask>()
const renderingPages = new Set<number>()
const renderKey = ref(0)
let isRendering = false
let shouldRestoreScroll = false
let shouldScrollToCurrentPage = false
let ignoreScrollUntil = 0
let savedScrollRatio = 0
let lastOutlinePosition: { pageNumber: number; pdfY: number } | null = null
let skipNextScrollToPage = false

const visiblePages = computed(() => {
  if (!props.pdfDoc) return []
  if (props.viewMode === 'single') {
    return [props.currentPage]
  }
  return Array.from({ length: props.pdfDoc.numPages }, (_, i) => i + 1)
})

function getPageAnnotations(pageNumber: number): PdfAnnotation[] {
  return props.annotations.filter(a => a.page_number === pageNumber)
}

async function renderPage(pageNumber: number) {
  if (!props.pdfDoc) return
  
  if (renderingPages.has(pageNumber)) return
  
  if (renderedPages.value.has(pageNumber)) return

  const canvas = canvasRefs.value[pageNumber]
  const textLayer = textLayerRefs.value[pageNumber]
  if (!canvas || !textLayer) return

  const pendingRender = pendingRenders.get(pageNumber)
  if (pendingRender) {
    try {
      pendingRender.cancel()
    } catch (e) {
      // ignore cancel errors
    }
    pendingRenders.delete(pageNumber)
  }

  renderingPages.add(pageNumber)

  try {
    const page = await props.pdfDoc.getPage(pageNumber)
    const viewport = page.getViewport({ scale: props.zoom })

    canvas.width = viewport.width
    canvas.height = viewport.height

    const context = canvas.getContext('2d')
    if (!context) {
      renderingPages.delete(pageNumber)
      return
    }

    const renderTask = page.render({
      canvasContext: context,
      viewport,
      canvas,
    })
    pendingRenders.set(pageNumber, renderTask)

    await renderTask.promise
    pendingRenders.delete(pageNumber)

    textLayer.innerHTML = ''
    textLayer.style.width = `${viewport.width}px`
    textLayer.style.height = `${viewport.height}px`

    const textContent = await page.getTextContent()
    
    const textLayerInstance = new pdfjsLib.TextLayer({
      textContentSource: textContent,
      container: textLayer,
      viewport,
    })
    await textLayerInstance.render()

    renderedPages.value.add(pageNumber)
    pageRendered.value[pageNumber] = true
  } catch (e: any) {
    if (e.name === 'RenderingCancelledException') {
      return
    }
    console.error(`Failed to render page ${pageNumber}:`, e)
  } finally {
    renderingPages.delete(pageNumber)
  }
}

async function renderVisiblePages() {
  isRendering = true
  const restoreScroll = shouldRestoreScroll
  const scrollToPage = shouldScrollToCurrentPage
  const scrollRatio = savedScrollRatio
  const outlinePos = lastOutlinePosition
  shouldRestoreScroll = false
  shouldScrollToCurrentPage = false
  savedScrollRatio = 0
  
  try {
    for (const pageNum of visiblePages.value) {
      await renderPage(pageNum)
    }
    
    await nextTick()
    
    if (props.viewMode === 'continuous' && scrollContainerRef.value) {
      if (restoreScroll) {
        if (outlinePos) {
          await scrollToY(outlinePos.pageNumber, outlinePos.pdfY)
        } else if (scrollRatio > 0) {
          const maxScroll = scrollContainerRef.value.scrollHeight - scrollContainerRef.value.clientHeight
          const targetScroll = maxScroll * scrollRatio
          ignoreScrollUntil = Date.now() + 300
          scrollContainerRef.value.scrollTo({
            top: targetScroll,
            behavior: 'instant'
          })
        }
      } else if (scrollToPage) {
        const pageElement = scrollContainerRef.value.querySelector(`[data-page="${props.currentPage}"]`)
        if (pageElement) {
          ignoreScrollUntil = Date.now() + 300
          pageElement.scrollIntoView({ behavior: 'instant', block: 'start' })
        }
      }
    }
    
    isRendering = false
  } catch (e) {
    isRendering = false
    console.error('Failed to render pages:', e)
  }
}

function clearRenderedPages() {
  pendingRenders.forEach((task) => {
    try {
      task.cancel()
    } catch (e) {
      // ignore cancel errors
    }
  })
  pendingRenders.clear()
  renderingPages.clear()
  renderedPages.value.clear()
  pageRendered.value = {}
  canvasRefs.value = {}
  textLayerRefs.value = {}
  renderKey.value++
}

function handleScroll() {
  if (props.viewMode !== 'continuous' || !scrollContainerRef.value) return
  if (isRendering) {
    console.log('[PdfViewer] handleScroll: skipped because isRendering')
    return
  }
  if (Date.now() < ignoreScrollUntil) {
    console.log('[PdfViewer] handleScroll: skipped because ignoreScrollUntil, now:', Date.now(), 'ignoreUntil:', ignoreScrollUntil)
    return
  }
  
  lastOutlinePosition = null

  const container = scrollContainerRef.value
  const containerRect = container.getBoundingClientRect()
  const pageElements = container.querySelectorAll('.page-container')
  
  let visiblePage = 1
  let maxVisibleArea = 0

  pageElements.forEach((el) => {
    const rect = el.getBoundingClientRect()
    const visibleTop = Math.max(rect.top, containerRect.top)
    const visibleBottom = Math.min(rect.bottom, containerRect.bottom)
    const visibleHeight = Math.max(0, visibleBottom - visibleTop)
    
    if (visibleHeight > maxVisibleArea) {
      maxVisibleArea = visibleHeight
      visiblePage = parseInt(el.getAttribute('data-page') || '1', 10)
    }
  })

  if (visiblePage !== props.currentPage) {
    emit('page-change', visiblePage)
  }
}

function handleTextSelect(data: { text: string; position: AnnotationPosition; clientX: number; clientY: number }, pageNumber: number) {
  emit('text-select', { ...data, pageNumber })
}

function handleAnnotationCreate(data: { type: AnnotationType; position: AnnotationPosition }, pageNumber: number) {
  emit('annotation-create', { ...data, pageNumber })
}

function handleResize() {
  if (!containerRef.value) return
  
  const rect = containerRef.value.getBoundingClientRect()
  emit('container-resize', { width: rect.width, height: rect.height })
}

function scrollToPage(pageNumber: number) {
  if (!scrollContainerRef.value || props.viewMode !== 'continuous') return
  if (skipNextScrollToPage) {
    skipNextScrollToPage = false
    return
  }

  const attemptScroll = () => {
    const pageElement = scrollContainerRef.value?.querySelector(`[data-page="${pageNumber}"]`)
    if (pageElement) {
      ignoreScrollUntil = Date.now() + 300
      pageElement.scrollIntoView({ behavior: 'instant', block: 'start' })
    } else {
      requestAnimationFrame(attemptScroll)
    }
  }

  nextTick(attemptScroll)
}

async function scrollToY(pageNumber: number, pdfY: number) {
  console.log('[PdfViewer] scrollToY called with pageNumber:', pageNumber, 'pdfY:', pdfY)
  console.log('[PdfViewer] scrollContainerRef.value:', !!scrollContainerRef.value, 'viewMode:', props.viewMode, 'pdfDoc:', !!props.pdfDoc)
  
  if (!scrollContainerRef.value || props.viewMode !== 'continuous' || !props.pdfDoc) {
    console.log('[PdfViewer] scrollToY early return - conditions not met')
    return
  }
  
  lastOutlinePosition = { pageNumber, pdfY }
  skipNextScrollToPage = true

  const pageElement = scrollContainerRef.value.querySelector(`[data-page="${pageNumber}"]`) as HTMLElement
  console.log('[PdfViewer] pageElement found:', !!pageElement)
  
  if (!pageElement) {
    console.log('[PdfViewer] pageElement not found, falling back to scrollToPage')
    scrollToPage(pageNumber)
    return
  }

  try {
    const page = await props.pdfDoc.getPage(pageNumber)
    const viewport = page.getViewport({ scale: 1 })
    
    const canvas = pageElement.querySelector('.pdf-canvas') as HTMLCanvasElement
    console.log('[PdfViewer] canvas found:', !!canvas)
    
    if (!canvas) {
      scrollToPage(pageNumber)
      return
    }
    
    const renderedHeight = canvas.height
    const pdfPageHeight = viewport.height
    const scale = renderedHeight / pdfPageHeight
    
    const webY = (pdfPageHeight - pdfY) * scale
    
    const containerRect = scrollContainerRef.value.getBoundingClientRect()
    const pageRect = pageElement.getBoundingClientRect()
    const pageTopInContainer = pageRect.top - containerRect.top + scrollContainerRef.value.scrollTop
    
    const targetScrollTop = pageTopInContainer + webY
    
    console.log('[PdfViewer] scroll calculation:', {
      pdfPageHeight,
      renderedHeight,
      scale,
      pdfY,
      webY,
      pageTopInContainer,
      targetScrollTop,
      currentScrollTop: scrollContainerRef.value.scrollTop,
      containerScrollHeight: scrollContainerRef.value.scrollHeight,
      containerClientHeight: scrollContainerRef.value.clientHeight
    })
    
    ignoreScrollUntil = Date.now() + 300
    scrollContainerRef.value.scrollTo({
      top: targetScrollTop,
      behavior: 'instant'
    })
    console.log('[PdfViewer] scrollTo executed, new scrollTop:', scrollContainerRef.value.scrollTop)
  } catch (e) {
    console.error('Failed to scroll to Y position:', e)
    scrollToPage(pageNumber)
  }
}

function retryLoad() {
  clearRenderedPages()
  renderVisiblePages()
}

let resizeObserver: ResizeObserver | null = null
let pendingRenderRequest = false

onMounted(() => {
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(handleResize)
    resizeObserver.observe(containerRef.value)
    handleResize()
  }
})

onUnmounted(() => {
  resizeObserver?.disconnect()
  clearRenderedPages()
})

onActivated(() => {
  if (props.pdfDoc) {
    clearRenderedPages()
    requestRender()
  }
})

function requestRender() {
  if (pendingRenderRequest) return
  pendingRenderRequest = true
  
  const attemptRender = () => {
    pendingRenderRequest = false
    const pages = visiblePages.value
    const allReady = pages.every(pageNum => 
      canvasRefs.value[pageNum] && textLayerRefs.value[pageNum]
    )
    
    if (allReady && pages.length > 0) {
      renderVisiblePages()
    } else if (props.pdfDoc) {
      pendingRenderRequest = true
      requestAnimationFrame(attemptRender)
    }
  }
  
  nextTick(attemptRender)
}

watch(() => props.pdfDoc, (newDoc) => {
  if (newDoc) {
    shouldScrollToCurrentPage = true
    clearRenderedPages()
    requestRender()
  }
}, { flush: 'post' })

watch(() => props.zoom, () => {
  if (scrollContainerRef.value) {
    const maxScroll = scrollContainerRef.value.scrollHeight - scrollContainerRef.value.clientHeight
    if (maxScroll > 0) {
      savedScrollRatio = scrollContainerRef.value.scrollTop / maxScroll
    }
  }
  shouldRestoreScroll = true
  clearRenderedPages()
  requestRender()
}, { flush: 'post' })

watch(() => props.viewMode, () => {
  clearRenderedPages()
  requestRender()
}, { flush: 'post' })

watch(() => props.currentPage, (newPage) => {
  if (props.viewMode === 'single') {
    clearRenderedPages()
    requestRender()
  } else if (props.isUserNavigating) {
    scrollToPage(newPage)
  }
})

defineExpose({
  scrollToPage,
  scrollToY,
  renderVisiblePages,
})
</script>

<style scoped>
.pdf-viewer {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: var(--pdf-bg);
}

.pdf-container {
  width: 100%;
  height: 100%;
  overflow: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  gap: 20px;
}

.pdf-container.single-page {
  justify-content: center;
}

.page-container {
  position: relative;
  background: white;
  box-shadow: var(--pdf-page-shadow);
  --user-unit: 1;
  --total-scale-factor: calc(var(--scale-factor) * var(--user-unit));
  --scale-round-x: 1px;
  --scale-round-y: 1px;
  overflow: visible;
}

.pdf-canvas {
  display: block;
}

.text-layer {
  position: absolute;
  text-align: initial;
  inset: 0;
  overflow: clip;
  opacity: 1;
  line-height: 1;
  z-index: 0;
  text-size-adjust: none;
  forced-color-adjust: none;
  transform-origin: 0 0;
  caret-color: CanvasText;
  --min-font-size: 1;
  --text-scale-factor: calc(var(--total-scale-factor) * var(--min-font-size));
  --min-font-size-inv: calc(1 / var(--min-font-size));
}

.text-layer :deep(span) {
  color: transparent;
  position: absolute;
  white-space: pre;
  cursor: text;
  transform-origin: 0% 0%;
}

.text-layer :deep(> :not(.markedContent)),
.text-layer :deep(.markedContent span:not(.markedContent)) {
  z-index: 1;
  --font-height: 0;
  font-size: calc(var(--text-scale-factor) * var(--font-height));
  --scale-x: 1;
  --rotate: 0deg;
  transform: rotate(var(--rotate)) scaleX(var(--scale-x)) scale(var(--min-font-size-inv));
}

.text-layer :deep(.markedContent) {
  display: contents;
}

.text-layer :deep(::selection) {
  background: rgba(0, 188, 212, 0.3);
}

.loading-overlay,
.error-overlay,
.empty-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  color: var(--text-secondary);
  gap: 16px;
}

.loading-overlay .spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-overlay svg,
.empty-overlay svg {
  width: 64px;
  height: 64px;
  color: var(--text-muted);
}

.error-overlay button {
  padding: 8px 24px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.error-overlay button:hover {
  opacity: 0.9;
}
</style>
