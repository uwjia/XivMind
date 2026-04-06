import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, defineComponent, h, type Ref } from 'vue'
import { mount } from '@vue/test-utils'
import { usePdfAnnotationLayer, type AnnotationLayerEmit } from './usePdfAnnotationLayer'
import type { AnnotationType, HighlightColor } from '@/types/pdf'

function createMockSelection(text: string, rect: DOMRect): Selection {
  const range = {
    getBoundingClientRect: () => rect,
  }
  return {
    isCollapsed: !text,
    toString: () => text,
    getRangeAt: () => range,
  } as unknown as Selection
}

function createTestComponent(layerRef: Ref<HTMLDivElement | null>, emit: AnnotationLayerEmit, props: {
  pageNumber: number
  zoom: number
  currentTool: AnnotationType | 'select' | null
  currentColor: HighlightColor
  strokeWidth: number
}) {
  return defineComponent({
    setup() {
      usePdfAnnotationLayer(layerRef, props, emit)
      return {}
    },
    render() {
      return h('div', { ref: layerRef }, 'Test Component')
    },
  })
}

describe('usePdfAnnotationLayer - handleTextSelection', () => {
  let layerRef: Ref<HTMLDivElement | null>
  let emit: AnnotationLayerEmit
  let props: {
    pageNumber: number
    zoom: number
    currentTool: AnnotationType | 'select' | null
    currentColor: HighlightColor
    strokeWidth: number
  }
  let getSelectionSpy: ReturnType<typeof vi.spyOn>

  beforeEach(() => {
    layerRef = ref<HTMLDivElement | null>(null)
    emit = vi.fn()
    props = {
      pageNumber: 1,
      zoom: 1,
      currentTool: null,
      currentColor: 'yellow',
      strokeWidth: 2,
    }
    getSelectionSpy = vi.spyOn(window, 'getSelection')
  })

  afterEach(() => {
    vi.restoreAllMocks()
    document.body.innerHTML = ''
  })

  it('should not emit when layerRef is null', async () => {
    const TestComponent = defineComponent({
      setup() {
        usePdfAnnotationLayer(layerRef, props, emit)
        return {}
      },
      render() {
        return h('div', 'No ref')
      },
    })
    
    mount(TestComponent)
    
    document.dispatchEvent(new MouseEvent('mouseup'))
    
    expect(emit).not.toHaveBeenCalled()
  })

  it('should not emit when event target is outside page-container', async () => {
    const outsideElement = document.createElement('div')
    document.body.appendChild(outsideElement)
    
    const pageContainer = document.createElement('div')
    pageContainer.className = 'page-container'
    
    const layerDiv = document.createElement('div')
    layerDiv.className = 'annotation-layer'
    pageContainer.appendChild(layerDiv)
    
    document.body.appendChild(pageContainer)
    
    layerRef.value = layerDiv
    
    const TestComponent = defineComponent({
      setup() {
        usePdfAnnotationLayer(layerRef, props, emit)
        return {}
      },
      render() {
        return h('div', 'Test')
      },
    })
    
    mount(TestComponent)
    
    const mockSelection = createMockSelection('selected text', new DOMRect(100, 100, 50, 20))
    getSelectionSpy.mockReturnValue(mockSelection)
    
    outsideElement.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
    
    expect(emit).not.toHaveBeenCalled()
  })

  it('should emit text-select when selection is inside page-container', async () => {
    const pageContainer = document.createElement('div')
    pageContainer.className = 'page-container'
    
    const layerDiv = document.createElement('div')
    layerDiv.className = 'annotation-layer'
    pageContainer.appendChild(layerDiv)
    
    const textLayer = document.createElement('div')
    textLayer.className = 'text-layer'
    pageContainer.appendChild(textLayer)
    
    const textSpan = document.createElement('span')
    textLayer.appendChild(textSpan)
    
    document.body.appendChild(pageContainer)
    layerRef.value = layerDiv
    
    const TestComponent = defineComponent({
      setup() {
        usePdfAnnotationLayer(layerRef, props, emit)
        return {}
      },
      render() {
        return h('div', 'Test')
      },
    })
    
    mount(TestComponent)
    
    const mockSelection = createMockSelection('selected text', new DOMRect(100, 100, 50, 20))
    getSelectionSpy.mockReturnValue(mockSelection)
    
    textSpan.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
    
    expect(emit).toHaveBeenCalledWith('text-select', expect.objectContaining({
      text: 'selected text',
    }))
  })

  it('should not emit when selection is collapsed (empty)', async () => {
    const pageContainer = document.createElement('div')
    pageContainer.className = 'page-container'
    
    const layerDiv = document.createElement('div')
    layerDiv.className = 'annotation-layer'
    pageContainer.appendChild(layerDiv)
    
    const textLayer = document.createElement('div')
    textLayer.className = 'text-layer'
    pageContainer.appendChild(textLayer)
    
    const textSpan = document.createElement('span')
    textLayer.appendChild(textSpan)
    
    document.body.appendChild(pageContainer)
    layerRef.value = layerDiv
    
    const TestComponent = defineComponent({
      setup() {
        usePdfAnnotationLayer(layerRef, props, emit)
        return {}
      },
      render() {
        return h('div', 'Test')
      },
    })
    
    mount(TestComponent)
    
    const mockSelection = createMockSelection('', new DOMRect(100, 100, 50, 20))
    getSelectionSpy.mockReturnValue(mockSelection)
    
    textSpan.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
    
    expect(emit).not.toHaveBeenCalled()
  })

  it('should not emit when event target is in a different page-container', async () => {
    const pageContainer1 = document.createElement('div')
    pageContainer1.className = 'page-container'
    
    const layerDiv = document.createElement('div')
    layerDiv.className = 'annotation-layer'
    pageContainer1.appendChild(layerDiv)
    
    const pageContainer2 = document.createElement('div')
    pageContainer2.className = 'page-container'
    
    const otherElement = document.createElement('div')
    pageContainer2.appendChild(otherElement)
    
    document.body.appendChild(pageContainer1)
    document.body.appendChild(pageContainer2)
    layerRef.value = layerDiv
    
    const TestComponent = defineComponent({
      setup() {
        usePdfAnnotationLayer(layerRef, props, emit)
        return {}
      },
      render() {
        return h('div', 'Test')
      },
    })
    
    mount(TestComponent)
    
    const mockSelection = createMockSelection('selected text', new DOMRect(100, 100, 50, 20))
    getSelectionSpy.mockReturnValue(mockSelection)
    
    otherElement.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
    
    expect(emit).not.toHaveBeenCalled()
  })
})
