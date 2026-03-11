<template>
  <div 
    ref="canvasRef"
    class="custom-canvas"
    :class="{ 'drag-over': isDragOver }"
    @mousedown="onCanvasMouseDown"
    @mousemove="onCanvasMouseMove"
    @mouseup="onCanvasMouseUp"
    @wheel="onWheel"
    @contextmenu.prevent
    @dblclick="onCanvasDoubleClick"
    @dragover.prevent="onDragOver"
    @dragleave="onDragLeave"
    @drop.prevent="onDrop"
  >
    <FloatingToolbar 
      :active-view="activeView || 'workflow'"
      :loading="loading"
      @change-view="$emit('change-view', $event)"
      @refresh-stats="loadStats"
    />
    
    <div 
      class="canvas-content"
      :style="contentStyle"
    >
      <svg class="connections-layer" :style="svgStyle">
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="5"
            refY="5"
            orient="auto"
          >
            <circle cx="5" cy="5" r="4" fill="#6B7280" />
          </marker>
        </defs>
        
        <g v-for="edge in edges" :key="`${edge.id}-${edgeUpdateKey}`">
          <path
            :d="getEdgePath(edge)"
            :stroke="getEdgeColor(edge)"
            stroke-width="2"
            fill="none"
            :marker-end="edge.targetPort ? 'url(#arrowhead)' : undefined"
            class="edge-path"
            :class="{ active: edge.active }"
            @click="onEdgeClick(edge)"
          />
        </g>
        
        <path
          v-if="tempConnection"
          :d="tempConnectionPath"
          :stroke="tempConnectionColor"
          stroke-width="2"
          stroke-dasharray="5,5"
          fill="none"
          class="temp-connection"
        />
      </svg>
      
      <div class="nodes-layer">
        <CustomNode
          v-for="node in nodes"
          :key="node.id"
          :ref="(el: any) => setNodeRef(node.id, el)"
          :node="node"
          :is-selected="selectedNodeId === node.id"
          :is-hover-valid-port="hoverValidPort"
          :agents="availableAgents"
          :skills="availableSkills"
          @select="onNodeSelect(node.id)"
          @drag-start="(e: MouseEvent) => onNodeDragStart(node.id, e)"
          @update:config="(key: string, value: any) => onNodeConfigUpdate(node.id, key, value)"
          @update:label="(label: string) => onNodeLabelUpdate(node.id, label)"
          @port-drag-start="(port: Port, portType: string, e: MouseEvent) => onPortDragStart(node.id, port, portType, e)"
          @port-drag-end="(port: Port, portType: string) => onPortDragEnd(node.id, port, portType)"
          @toggle-collapse="onNodeToggleCollapse(node.id)"
        />
      </div>
    </div>
    
    <div class="canvas-controls">
      <button class="zoom-btn" @click="zoomIn" title="Zoom In">+</button>
      <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
      <button class="zoom-btn" @click="zoomOut" title="Zoom Out">−</button>
      <button class="zoom-btn" @click="resetView" title="Reset View">⟲</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import CustomNode from './CustomNode.vue'
import FloatingToolbar from './FloatingToolbar.vue'
import { useTeam } from '@/composables/useTeam'
import type { WorkflowNode, WorkflowEdge, Port, PortDataType } from '@/types/workflow'
import { areTypesCompatible } from '@/types/workflow'

const props = defineProps<{
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  selectedNodeId?: string | null
  availableAgents?: string[]
  availableSkills?: string[]
  activeView?: 'task' | 'workflow'
}>()

const emit = defineEmits<{
  (e: 'node-select', nodeId: string): void
  (e: 'node-drag', nodeId: string, position: { x: number; y: number }): void
  (e: 'node-config-update', nodeId: string, key: string, value: any): void
  (e: 'node-label-update', nodeId: string, label: string): void
  (e: 'edge-create', sourceId: string, targetId: string, sourcePort: string, targetPort: string): void
  (e: 'edge-delete', edgeId: string): void
  (e: 'canvas-click'): void
  (e: 'canvas-double-click', position: { x: number; y: number }): void
  (e: 'node-drop', nodeType: string, position: { x: number; y: number }): void
  (e: 'change-view', view: 'task' | 'workflow'): void
}>()

const { loading, loadStats } = useTeam()

const canvasRef = ref<HTMLElement | null>(null)
const nodeElements = ref<Map<string, HTMLElement>>(new Map())

const zoom = ref(1)
const pan = ref({ x: 0, y: 0 })
const isDraggingCanvas = ref(false)
const isDraggingNode = ref(false)
const draggedNodeId = ref<string | null>(null)
const dragStartPos = ref({ x: 0, y: 0 })
const nodeStartPos = ref({ x: 0, y: 0 })

const isConnecting = ref(false)
const connectingFrom = ref<{ nodeId: string; port: Port; portType: string } | null>(null)
const tempConnection = ref<{ x1: number; y1: number; x2: number; y2: number } | null>(null)
const hoverValidPort = ref<{ portId: string; type: string } | null>(null)
const edgeUpdateKey = ref(0)

watch([zoom, pan], () => {
  nextTick(() => {
    edgeUpdateKey.value++
  })
})

const contentStyle = computed(() => ({
  transform: `translate(${pan.value.x}px, ${pan.value.y}px) scale(${zoom.value})`,
  transformOrigin: '0 0',
}))

const svgStyle = computed(() => ({
  position: 'absolute' as const,
  top: '0',
  left: '0',
  width: '100%',
  height: '100%',
  pointerEvents: isConnecting.value ? 'none' as const : 'auto' as const,
}))

const tempConnectionPath = computed(() => {
  if (!tempConnection.value) return ''
  return getBezierPath(
    tempConnection.value.x1,
    tempConnection.value.y1,
    tempConnection.value.x2,
    tempConnection.value.y2
  )
})

const tempConnectionColor = computed(() => {
  if (!connectingFrom.value) return '#8B5CF6'
  return getPortColor(connectingFrom.value.port.dataType)
})

function setNodeRef(nodeId: string, el: any) {
  if (el) {
    const domEl = el.$el as HTMLElement
    if (domEl) {
      nodeElements.value.set(nodeId, domEl)
    }
  } else {
    nodeElements.value.delete(nodeId)
  }
}

function getPortColor(dataType: PortDataType): string {
  const colors: Record<PortDataType, string> = {
    text: '#3B82F6',
    data: '#8B5CF6',
    paper: '#10B981',
    analysis: '#F59E0B',
    task: '#EC4899',
    result: '#14B8A6',
    any: '#6B7280',
  }
  return colors[dataType] || colors.any
 }

function getEdgeColor(edge: WorkflowEdge): string {
  const sourceNode = props.nodes.find(n => n.id === edge.source)
  if (sourceNode && edge.sourcePort) {
    const port = sourceNode.outputs.find(p => p.id === edge.sourcePort)
    if (port) return getPortColor(port.dataType)
  }
  return '#6B7280'
}

function getEdgePath(edge: WorkflowEdge): string {
  const sourceNode = props.nodes.find(n => n.id === edge.source)
  const targetNode = props.nodes.find(n => n.id === edge.target)
  if (!sourceNode || !targetNode) return ''
  
  const sourceEl = nodeElements.value.get(edge.source)
  const targetEl = nodeElements.value.get(edge.target)
  if (!sourceEl || !targetEl) return ''
  
  let x1 = sourceNode.position.x + sourceEl.offsetWidth
  let y1 = sourceNode.position.y + 30
  let x2 = targetNode.position.x
  let y2 = targetNode.position.y + 30
  
  if (edge.sourcePort && sourceEl) {
    const portEl = findVisiblePort(sourceEl, edge.sourcePort)
    if (portEl) {
      const rect = portEl.getBoundingClientRect()
      const canvasRect = canvasRef.value!.getBoundingClientRect()
      x1 = (rect.left + rect.width / 2 - canvasRect.left - pan.value.x) / zoom.value
      y1 = (rect.top + rect.height / 2 - canvasRect.top - pan.value.y) / zoom.value
    }
  }
  
  if (edge.targetPort && targetEl) {
    const portEl = findVisiblePort(targetEl, edge.targetPort)
    if (portEl) {
      const rect = portEl.getBoundingClientRect()
      const canvasRect = canvasRef.value!.getBoundingClientRect()
      x2 = (rect.left + rect.width / 2 - canvasRect.left - pan.value.x) / zoom.value
      y2 = (rect.top + rect.height / 2 - canvasRect.top - pan.value.y) / zoom.value
    }
  }
  
  return getBezierPath(x1, y1, x2, y2)
}

function findVisiblePort(nodeEl: HTMLElement, portId: string): HTMLElement | null {
  const ports = nodeEl.querySelectorAll(`[data-port-id="${portId}"]`)
  for (const port of ports) {
    const el = port as HTMLElement
    if (el.offsetParent !== null) {
      return el
    }
  }
  return ports[0] as HTMLElement || null
}

function getBezierPath(x1: number, y1: number, x2: number, y2: number): string {
  const dx = Math.abs(x2 - x1) * 0.5
  return `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`
}

 function onCanvasMouseDown(event: MouseEvent) {
  if (event.button !== 0) return
  if ((event.target as HTMLElement).closest('.custom-node')) return
  if ((event.target as HTMLElement).closest('.edge-path')) return
  
  isDraggingCanvas.value = true
  dragStartPos.value = { x: event.clientX - pan.value.x, y: event.clientY - pan.value.y }
  emit('canvas-click')
}

 function onCanvasMouseMove(event: MouseEvent) {
  if (isDraggingCanvas.value) {
    pan.value = {
      x: event.clientX - dragStartPos.value.x,
      y: event.clientY - dragStartPos.value.y,
    }
  } else if (isDraggingNode.value && draggedNodeId.value) {
    const node = props.nodes.find(n => n.id === draggedNodeId.value)
    if (node) {
      const dx = (event.clientX - dragStartPos.value.x) / zoom.value
      const dy = (event.clientY - dragStartPos.value.y) / zoom.value
      emit('node-drag', draggedNodeId.value, {
        x: nodeStartPos.value.x + dx,
        y: nodeStartPos.value.y + dy,
      })
    }
  } else if (isConnecting.value && connectingFrom.value) {
    const canvasRect = canvasRef.value!.getBoundingClientRect()
    const x2 = (event.clientX - canvasRect.left - pan.value.x) / zoom.value
    const y2 = (event.clientY - canvasRect.top - pan.value.y) / zoom.value
    
    const sourceNode = props.nodes.find(n => n.id === connectingFrom.value!.nodeId)
    if (sourceNode) {
      const sourceEl = nodeElements.value.get(sourceNode.id)
      if (sourceEl && connectingFrom.value.port) {
        const portEl = sourceEl.querySelector(`[data-port-id="${connectingFrom.value.port.id}"]`) as HTMLElement
        if (portEl) {
          const portRect = portEl.getBoundingClientRect()
          const x1 = (portRect.left + portRect.width / 2 - canvasRect.left - pan.value.x) / zoom.value
          const y1 = (portRect.top + portRect.height / 2 - canvasRect.top - pan.value.y) / zoom.value
          tempConnection.value = { x1, y1, x2, y2 }
        }
      }
    }
    
    const targetPort = findPortAtPosition(event.clientX, event.clientY)
    if (targetPort && canConnect(connectingFrom.value, targetPort)) {
      hoverValidPort.value = { portId: targetPort.port.id, type: targetPort.type }
    } else {
      hoverValidPort.value = null
    }
  }
}

 function onCanvasMouseUp(event: MouseEvent) {
  if (isDraggingCanvas.value) {
    isDraggingCanvas.value = false
  } else if (isDraggingNode.value) {
    isDraggingNode.value = false
    draggedNodeId.value = null
  } else if (isConnecting.value) {
    const targetPort = findPortAtPosition(event.clientX, event.clientY)
    if (targetPort && connectingFrom.value && canConnect(connectingFrom.value, targetPort)) {
      const { nodeId: sourceId, port: sourcePort, portType: sourceType } = connectingFrom.value
      const { nodeId: targetId, port: targetPortObj, type: targetType } = targetPort
      
      if (sourceType === 'output' && targetType === 'input') {
        emit('edge-create', sourceId, targetId, sourcePort.id, targetPortObj.id)
      } else if (sourceType === 'input' && targetType === 'output') {
        emit('edge-create', targetId, sourceId, targetPortObj.id, sourcePort.id)
      }
    }
    
    isConnecting.value = false
    connectingFrom.value = null
    tempConnection.value = null
    hoverValidPort.value = null
  }
}

 function findPortAtPosition(clientX: number, clientY: number): { nodeId: string; port: Port; type: string } | null {
  const elements = document.elementsFromPoint(clientX, clientY)
  for (const el of elements) {
    const portEl = (el as HTMLElement).closest('[data-port-id]') as HTMLElement
    if (portEl) {
      const portId = portEl.dataset.portId
      const nodeId = portEl.dataset.nodeId
      const portType = portEl.dataset.portType
      if (portId && nodeId && portType) {
        const node = props.nodes.find(n => n.id === nodeId)
        if (node) {
          const ports = portType === 'input' ? node.inputs : node.outputs
          const port = ports.find(p => p.id === portId)
          if (port) {
            return { nodeId, port, type: portType }
          }
        }
      }
    }
  }
  return null
}

 function canConnect(
  from: { nodeId: string; port: Port; portType: string },
  to: { nodeId: string; port: Port; type: string }
): boolean {
  if (from.nodeId === to.nodeId) return false
  if (from.portType === to.type) return false
  
  const sourcePort = from.portType === 'output' ? from.port : to.port
  const targetPort = from.portType === 'input' ? from.port : to.port
  
  return areTypesCompatible(sourcePort.dataType, targetPort.dataType)
}

 function onWheel(event: WheelEvent) {
  event.preventDefault()
  const delta = event.deltaY > 0 ? 0.9 : 1.1
  const newZoom = Math.min(2, Math.max(0.25, zoom.value * delta))
  
  const rect = canvasRef.value!.getBoundingClientRect()
  const mouseX = event.clientX - rect.left
  const mouseY = event.clientY - rect.top
  
  pan.value.x = mouseX - (mouseX - pan.value.x) * (newZoom / zoom.value)
  pan.value.y = mouseY - (mouseY - pan.value.y) * (newZoom / zoom.value)
  zoom.value = newZoom
}

 function onCanvasDoubleClick(event: MouseEvent) {
  if ((event.target as HTMLElement).closest('.custom-node')) return
  
  const rect = canvasRef.value!.getBoundingClientRect()
  const x = (event.clientX - rect.left - pan.value.x) / zoom.value
  const y = (event.clientY - rect.top - pan.value.y) / zoom.value
  emit('canvas-double-click', { x, y })
}

 function onNodeSelect(nodeId: string) {
  emit('node-select', nodeId)
}

 function onNodeDragStart(nodeId: string, event: MouseEvent) {
  isDraggingNode.value = true
  draggedNodeId.value = nodeId
  const node = props.nodes.find(n => n.id === nodeId)
  if (node) {
    nodeStartPos.value = { ...node.position }
    dragStartPos.value = { x: event.clientX, y: event.clientY }
  }
}

 function onNodeConfigUpdate(nodeId: string, key: string, value: any) {
  emit('node-config-update', nodeId, key, value)
}

function onNodeLabelUpdate(nodeId: string, label: string) {
  emit('node-label-update', nodeId, label)
}

function onPortDragStart(nodeId: string, port: Port, portType: string, _event: MouseEvent) {
  isConnecting.value = true
  connectingFrom.value = { nodeId, port, portType }
}

function onPortDragEnd(nodeId: string, port: Port, portType: string) {
  if (isConnecting.value && connectingFrom.value) {
    const targetPort = { nodeId, port, type: portType }
    if (canConnect(connectingFrom.value, targetPort)) {
      const { nodeId: sourceId, port: sourcePort, portType: sourceType } = connectingFrom.value
      
      if (sourceType === 'output' && portType === 'input') {
        emit('edge-create', sourceId, nodeId, sourcePort.id, port.id)
      } else if (sourceType === 'input' && portType === 'output') {
        emit('edge-create', nodeId, sourceId, port.id, sourcePort.id)
      }
    }
  }
  
  isConnecting.value = false
  connectingFrom.value = null
  tempConnection.value = null
  hoverValidPort.value = null
}

 function onNodeToggleCollapse(_nodeId: string) {
   nextTick(() => {
     edgeUpdateKey.value++
   })
 }

 function onEdgeClick(edge: WorkflowEdge) {
  emit('edge-delete', edge.id)
}

 function zoomIn() {
  zoom.value = Math.min(2, zoom.value * 1.2)
}

 function zoomOut() {
  zoom.value = Math.max(0.25, zoom.value / 1.2)
}

 function resetView() {
  zoom.value = 1
  pan.value = { x: 0, y: 0 }
}

 function fitView() {
  if (props.nodes.length === 0) {
    resetView()
    return
  }
  
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
  for (const node of props.nodes) {
    const el = nodeElements.value.get(node.id)
    const w = el?.offsetWidth || 200
    const h = el?.offsetHeight || 100
    minX = Math.min(minX, node.position.x)
    minY = Math.min(minY, node.position.y)
    maxX = Math.max(maxX, node.position.x + w)
    maxY = Math.max(maxY, node.position.y + h)
  }
  
  const rect = canvasRef.value!.getBoundingClientRect()
  const padding = 50
  const contentWidth = maxX - minX + padding * 2
  const contentHeight = maxY - minY + padding * 2
  
  const scaleX = rect.width / contentWidth
  const scaleY = rect.height / contentHeight
  zoom.value = Math.min(1, Math.min(scaleX, scaleY))
  
  pan.value = {
    x: (rect.width - contentWidth * zoom.value) / 2 - minX * zoom.value + padding * zoom.value,
    y: (rect.height - contentHeight * zoom.value) / 2 - minY * zoom.value + padding * zoom.value,
  }
}

defineExpose({
  fitView,
  zoomIn,
  zoomOut,
  resetView,
})

const isDragOver = ref(false)

function onDragOver(event: DragEvent) {
  event.preventDefault()
  isDragOver.value = true
}

function onDragLeave() {
  isDragOver.value = false
}

function onDrop(event: DragEvent) {
  isDragOver.value = false
  
  const nodeType = event.dataTransfer?.getData('nodeType')
  if (!nodeType) return
  
  const rect = canvasRef.value!.getBoundingClientRect()
  const x = (event.clientX - rect.left - pan.value.x) / zoom.value
  const y = (event.clientY - rect.top - pan.value.y) / zoom.value
  
  emit('node-drop', nodeType, { x, y })
}
</script>

<style scoped>
.custom-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: var(--bg-primary);
  background-image: 
    radial-gradient(circle, var(--border-color) 1px, transparent 1px);
  background-size: 20px 20px;
  cursor: grab;
}

.custom-canvas:active {
  cursor: grabbing;
}

.custom-canvas.drag-over {
  background-color: rgba(139, 92, 246, 0.05);
  outline: 2px dashed var(--primary-color);
  outline-offset: -2px;
}

.canvas-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: visible;
}

.edge-path {
  cursor: pointer;
  pointer-events: stroke;
  transition: stroke-width 0.2s;
}

.edge-path:hover {
  stroke-width: 3;
}

.edge-path.active {
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.temp-connection {
  pointer-events: none;
}

.nodes-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.canvas-controls {
  position: absolute;
  bottom: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-secondary);
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.zoom-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.zoom-btn:hover {
  background: var(--bg-primary);
  border-color: var(--primary-color);
}

.zoom-level {
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 40px;
  text-align: center;
}
</style>
