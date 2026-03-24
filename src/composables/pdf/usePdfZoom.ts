import { ref, computed, type Ref } from 'vue'

const MIN_ZOOM_VALUE = 0.25
const MAX_ZOOM_VALUE = 5
const ZOOM_STEP_VALUE = 0.25

export function usePdfZoom(
  containerWidth: Ref<number>,
  containerHeight: Ref<number>,
  pageWidth: Ref<number>,
  pageHeight: Ref<number>
) {
  const zoom = ref(1)
  const fitMode = ref<'width' | 'page' | 'custom'>('width')

  const zoomPercentage = computed(() => Math.round(zoom.value * 100))

  function setZoom(value: number) {
    zoom.value = Math.max(MIN_ZOOM_VALUE, Math.min(MAX_ZOOM_VALUE, value))
    fitMode.value = 'custom'
  }

  function zoomIn() {
    setZoom(zoom.value + ZOOM_STEP_VALUE)
  }

  function zoomOut() {
    setZoom(zoom.value - ZOOM_STEP_VALUE)
  }

  function fitToWidth() {
    if (containerWidth.value > 0 && pageWidth.value > 0) {
      const newZoom = (containerWidth.value - 40) / pageWidth.value
      zoom.value = Math.max(MIN_ZOOM_VALUE, Math.min(MAX_ZOOM_VALUE, newZoom))
      fitMode.value = 'width'
    }
  }

  function fitToPage() {
    if (containerWidth.value > 0 && containerHeight.value > 0 && 
        pageWidth.value > 0 && pageHeight.value > 0) {
      const widthRatio = (containerWidth.value - 40) / pageWidth.value
      const heightRatio = (containerHeight.value - 40) / pageHeight.value
      const newZoom = Math.min(widthRatio, heightRatio)
      zoom.value = Math.max(MIN_ZOOM_VALUE, Math.min(MAX_ZOOM_VALUE, newZoom))
      fitMode.value = 'page'
    }
  }

  function resetZoom() {
    zoom.value = 1
    fitMode.value = 'custom'
  }

  return {
    zoom,
    fitMode,
    zoomPercentage,
    setZoom,
    zoomIn,
    zoomOut,
    fitToWidth,
    fitToPage,
    resetZoom,
  }
}
