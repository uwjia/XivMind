import * as pdfjsLib from 'pdfjs-dist'
import { ref, shallowRef, computed, onUnmounted } from 'vue'
import type { PdfOutlineItem, PdfThumbnail } from '@/types/pdf'

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.mjs',
  import.meta.url
).toString()

export function usePdfReader() {
  const pdfDoc = shallowRef<pdfjsLib.PDFDocumentProxy | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalPages = ref(0)
  const outline = ref<PdfOutlineItem[]>([])
  const thumbnails = ref<PdfThumbnail[]>([])

  const isLoaded = computed(() => pdfDoc.value !== null)

  async function loadPdf(source: string | ArrayBuffer | Blob): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      let data: ArrayBuffer | undefined
      let url: string | undefined

      if (typeof source === 'string') {
        url = source
      } else if (source instanceof ArrayBuffer) {
        data = source
      } else if (source instanceof Blob) {
        data = await source.arrayBuffer()
      }

      const loadingTask = pdfjsLib.getDocument({
        data,
        url,
        cMapUrl: 'https://unpkg.com/pdfjs-dist@4.0.379/cmaps/',
        cMapPacked: true,
      })

      pdfDoc.value = await loadingTask.promise
      totalPages.value = pdfDoc.value.numPages

      await loadOutline()
      
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load PDF'
      pdfDoc.value = null
      return false
    } finally {
      loading.value = false
    }
  }

  async function loadOutline(): Promise<void> {
    if (!pdfDoc.value) return

    try {
      const outlineData = await pdfDoc.value.getOutline()
      if (outlineData) {
        outline.value = await processOutlineItems(outlineData)
      }
    } catch (e) {
      console.error('Failed to load outline:', e)
    }
  }

  async function processOutlineItems(items: any[]): Promise<PdfOutlineItem[]> {
    const result: PdfOutlineItem[] = []

    for (const item of items) {
      let dest: number | null = null
      let y: number | null = null
      
      if (item.dest) {
        const resolved = await resolveDestination(item.dest)
        dest = resolved.page
        y = resolved.y
      } else if (item.ref) {
        try {
          const pageIndex = await pdfDoc.value!.getPageIndex(item.ref)
          dest = pageIndex + 1
        } catch {
          // ignore
        }
      }
      
      const outlineItem: PdfOutlineItem = {
        title: item.title,
        dest,
        y,
        items: [],
      }
      
      if (item.items && item.items.length > 0) {
        outlineItem.items = await processOutlineItems(item.items)
      }
      
      result.push(outlineItem)
    }

    return result
  }

  async function resolveDestination(dest: any): Promise<{ page: number | null; y: number | null }> {
    if (!pdfDoc.value) return { page: null, y: null }
    
    try {
      let destArray: any[] | null = null
      
      if (typeof dest === 'string') {
        destArray = await pdfDoc.value.getDestination(dest)
      } else if (Array.isArray(dest)) {
        destArray = dest
      }
      
      if (destArray && destArray.length >= 3) {
        const destRef = destArray[0]
        let page: number | null = null
        
        if (typeof destRef === 'object' && destRef !== null) {
          if ('num' in destRef) {
            const pageIndex = await pdfDoc.value.getPageIndex(destRef)
            page = pageIndex + 1
          } else {
            try {
              const pageIndex = await pdfDoc.value.getPageIndex(destRef)
              page = pageIndex + 1
            } catch {
              // ignore
            }
          }
        } else if (typeof destRef === 'number') {
          page = destRef + 1
        }
        
        let y: number | null = null
        if (destArray.length >= 4 && typeof destArray[3] === 'number') {
          y = destArray[3]
        }
        
        return { page, y }
      }
    } catch (e) {
      console.error('Failed to resolve destination:', e)
    }
    
    return { page: null, y: null }
  }

  async function generateThumbnails(maxWidth: number = 150): Promise<void> {
    if (!pdfDoc.value) return

    thumbnails.value = []

    for (let i = 1; i <= totalPages.value; i++) {
      try {
        const page = await pdfDoc.value.getPage(i)
        const viewport = page.getViewport({ scale: 1 })
        const scale = maxWidth / viewport.width
        const scaledViewport = page.getViewport({ scale })

        const canvas = document.createElement('canvas')
        const context = canvas.getContext('2d')
        if (!context) continue

        canvas.width = scaledViewport.width
        canvas.height = scaledViewport.height

        await page.render({
          canvasContext: context,
          viewport: scaledViewport,
          canvas,
        }).promise

        thumbnails.value.push({
          page_number: i,
          src: canvas.toDataURL('image/jpeg', 0.7),
          width: scaledViewport.width,
          height: scaledViewport.height,
        })
      } catch (e) {
        console.error(`Failed to generate thumbnail for page ${i}:`, e)
      }
    }
  }

  async function getPage(pageNumber: number): Promise<pdfjsLib.PDFPageProxy | null> {
    if (!pdfDoc.value || pageNumber < 1 || pageNumber > totalPages.value) {
      return null
    }
    return pdfDoc.value.getPage(pageNumber)
  }

  function cleanup() {
    pdfDoc.value = null
    totalPages.value = 0
    outline.value = []
    thumbnails.value = []
    error.value = null
  }

  onUnmounted(() => {
    cleanup()
  })

  return {
    pdfDoc,
    loading,
    error,
    totalPages,
    outline,
    thumbnails,
    isLoaded,
    loadPdf,
    loadOutline,
    generateThumbnails,
    getPage,
    cleanup,
  }
}
