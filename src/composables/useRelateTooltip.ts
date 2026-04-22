import { ref, nextTick, watch } from 'vue'
import type { RelatedPaper } from '@/composables/useRelatedPapers'

export function useRelateTooltip() {
  const tooltipVisible = ref(false)
  const tooltipPaper = ref<RelatedPaper | null>(null)
  const tooltipStyle = ref<Record<string, string>>({})
  const isTooltipPinned = ref(false)
  const pinnedPaper = ref<RelatedPaper | null>(null)
  const isAbstractExpanded = ref(false)
  const tooltipRef = ref<HTMLElement | null>(null)

  const updateTooltipPosition = (rect: DOMRect) => {
    const viewportWidth = window.innerWidth
    const tooltipWidth = 400
    const gap = 12
    
    let left = rect.right + gap
    if (left + tooltipWidth > viewportWidth) {
      left = rect.left - gap - tooltipWidth
    }
    if (left < 0) {
      left = gap
    }
    
    tooltipStyle.value = {
      left: `${left}px`,
      top: `${rect.top}px`,
      maxWidth: `${tooltipWidth}px`
    }
  }

  const adjustTooltipPosition = () => {
    if (!tooltipRef.value) return
    
    const viewportHeight = window.innerHeight
    const gap = 12
    const tooltipRect = tooltipRef.value.getBoundingClientRect()
    
    if (tooltipRect.bottom > viewportHeight - gap) {
      const newTop = Math.max(gap, viewportHeight - tooltipRect.height - gap)
      tooltipStyle.value = {
        ...tooltipStyle.value,
        top: `${newTop}px`,
        maxHeight: `calc(100vh - ${gap * 2}px)`
      }
    }
  }

  const showTooltip = (paper: RelatedPaper, event: MouseEvent) => {
    if (isTooltipPinned.value) return
    
    tooltipPaper.value = paper
    tooltipVisible.value = true
    
    const target = event.target as HTMLElement
    const rect = target.closest('.paper-item')?.getBoundingClientRect()
    
    if (rect) {
      updateTooltipPosition(rect)
      nextTick(() => {
        adjustTooltipPosition()
      })
    }
  }

  const hideTooltip = () => {
    if (isTooltipPinned.value) return
    
    tooltipVisible.value = false
    tooltipPaper.value = null
  }

  const togglePinnedTooltip = (paper: RelatedPaper, event: MouseEvent) => {
    if (isTooltipPinned.value && pinnedPaper.value?.id === paper.id) {
      closePinnedTooltip()
      return
    }
    
    isTooltipPinned.value = true
    pinnedPaper.value = paper
    tooltipPaper.value = paper
    tooltipVisible.value = true
    
    const target = event.target as HTMLElement
    const rect = target.closest('.paper-item')?.getBoundingClientRect()
    
    if (rect) {
      updateTooltipPosition(rect)
      nextTick(() => {
        adjustTooltipPosition()
      })
    }
  }

  const closePinnedTooltip = () => {
    isTooltipPinned.value = false
    pinnedPaper.value = null
    tooltipVisible.value = false
    tooltipPaper.value = null
    isAbstractExpanded.value = false
  }

  const truncateAbstract = (abstract: string, maxLength: number = 300) => {
    if (!abstract) return ''
    if (abstract.length <= maxLength) return abstract
    return abstract.slice(0, maxLength) + '...'
  }

  const isAbstractLong = (abstract: string, maxLength: number = 300) => {
    return abstract && abstract.length > maxLength
  }

  const toggleAbstractExpand = () => {
    isAbstractExpanded.value = !isAbstractExpanded.value
  }

  const formatDate = (dateStr: string) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString()
  }

  watch(isAbstractExpanded, () => {
    nextTick(() => {
      adjustTooltipPosition()
    })
  })

  return {
    tooltipVisible,
    tooltipPaper,
    tooltipStyle,
    isTooltipPinned,
    pinnedPaper,
    isAbstractExpanded,
    tooltipRef,
    showTooltip,
    hideTooltip,
    togglePinnedTooltip,
    closePinnedTooltip,
    truncateAbstract,
    isAbstractLong,
    toggleAbstractExpand,
    formatDate
  }
}
