<template>
  <div class="workflow-canvas" ref="canvasContainer">
    <FloatingToolbar 
      :active-view="activeView || 'workflow'"
      :loading="loading"
      @change-view="$emit('change-view', $event)"
      @refresh-stats="loadStats"
    />
    
    <div class="canvas-toolbar">
      <button class="zoom-btn" @click="zoomIn" title="Zoom In">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          <line x1="11" y1="8" x2="11" y2="14"/>
          <line x1="8" y1="11" x2="14" y2="11"/>
        </svg>
      </button>
      <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
      <button class="zoom-btn" @click="zoomOut" title="Zoom Out">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          <line x1="8" y1="11" x2="14" y2="11"/>
        </svg>
      </button>
      <button class="zoom-btn" @click="resetView" title="Reset View">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
          <path d="M3 3v5h5"/>
        </svg>
      </button>
    </div>
    
    <div class="canvas-area" ref="networkContainer"></div>
    
    <div v-if="isConnecting" class="connection-indicator">
      <span>Click on a target node to connect</span>
      <button class="cancel-btn" @click="cancelConnection">Cancel</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Network } from 'vis-network/standalone'
import { DataSet } from 'vis-data/standalone'
import type { Data, Node, Edge, Options } from 'vis-network/standalone'
import { useWorkflow } from '@/composables/useWorkflow'
import { useTeam } from '@/composables/useTeam'
import { getNodeTypeInfo, NODE_PORT_DEFINITIONS, type WorkflowNodeType } from '@/types/workflow'
import FloatingToolbar from '@/components/team/FloatingToolbar.vue'

const {
  nodes,
  edges,
  isExecuting,
  addNode,
  addEdge,
  selectNode,
  selectEdge,
  clearSelection,
  updateNodePosition,
} = useWorkflow()

const { loading, loadStats } = useTeam()

const props = defineProps<{
  activeView?: 'task' | 'workflow'
}>()

const emit = defineEmits<{
  (e: 'node-selected', nodeId: string): void
  (e: 'edge-selected', edgeId: string): void
  (e: 'canvas-click'): void
  (e: 'change-view', view: 'task' | 'workflow'): void
}>()

const networkContainer = ref<HTMLElement | null>(null)
const network = ref<Network | null>(null)
const nodesDataSet = ref<DataSet<Node> | null>(null)
const edgesDataSet = ref<DataSet<Edge> | null>(null)
const zoom = ref(1)
const isConnecting = ref(false)
const connectingFrom = ref<string | null>(null)
const isUpdatingFromWatch = ref(false)

const nodeColors: Record<string, { background: string; border: string }> = {
  input: { background: '#3B82F6', border: '#2563EB' },
  analyze: { background: '#8B5CF6', border: '#7C3AED' },
  decompose: { background: '#F59E0B', border: '#D97706' },
  agent: { background: '#10B981', border: '#059669' },
  condition: { background: '#6366F1', border: '#4F46E5' },
  parallel: { background: '#EC4899', border: '#DB2777' },
  synthesize: { background: '#14B8A6', border: '#0D9488' },
  output: { background: '#EF4444', border: '#DC2626' },
  tool: { background: '#64748B', border: '#475569' },
  skill: { background: '#F97316', border: '#EA580C' },
}

function getVisNodes(): Node[] {
  return nodes.value.map(node => {
    const typeInfo = getNodeTypeInfo(node.type)
    const colors = nodeColors[node.type] || nodeColors.input
    const portDefs = NODE_PORT_DEFINITIONS[node.type]
    
    const inputLabels = portDefs.inputs.map((p) => `▸ ${p.label}`).join('\n')
    const outputLabels = portDefs.outputs.map((p) => `${p.label} ▸`).join('\n')
    
    const portInfo = []
    if (inputLabels) portInfo.push(inputLabels)
    if (outputLabels) portInfo.push(outputLabels)
    
    const fullLabel = portInfo.length > 0 
      ? `${node.label}\n${portInfo.join('\n')}`
      : node.label
    
    let borderWidth = 2
    let borderColor = colors.border
    let shadowColor = 'rgba(0,0,0,0.1)'
    
    if (node.status === 'running') {
      borderWidth = 3
      borderColor = '#3B82F6'
      shadowColor = 'rgba(59, 130, 246, 0.3)'
    } else if (node.status === 'success') {
      borderWidth = 2
      borderColor = '#10B981'
      shadowColor = 'rgba(16, 185, 129, 0.2)'
    } else if (node.status === 'error') {
      borderWidth = 2
      borderColor = '#EF4444'
      shadowColor = 'rgba(239, 68, 68, 0.2)'
    }
    
    return {
      id: node.id,
      label: fullLabel,
      x: node.position.x,
      y: node.position.y,
      color: {
        background: colors.background,
        border: borderColor,
        highlight: {
          background: colors.background,
          border: '#8B5CF6',
        },
      },
      borderWidth,
      shadow: {
        enabled: true,
        color: shadowColor,
        size: 15,
        x: 0,
        y: 2,
      },
      font: {
        color: '#FFFFFF',
        size: 12,
        face: 'Inter, system-ui, sans-serif',
        align: 'left',
      },
      shape: 'box',
      shapeProperties: {
        borderRadius: 8,
      },
      margin: {
        top: 10,
        right: 15,
        bottom: 10,
        left: 15,
      },
      title: `${typeInfo.description}\nStatus: ${node.status}`,
    }
  })
}

function getVisEdges(): Edge[] {
  return edges.value.map(edge => {
    const sourceNode = nodes.value.find(n => n.id === edge.source)
    
    let edgeColor = '#6B7280'
    let edgeWidth = 2
    
    if (sourceNode && edge.sourcePort) {
      const sourcePort = sourceNode.outputs.find(p => p.id === edge.sourcePort)
      if (sourcePort) {
        edgeColor = getPortColorByType(sourcePort.dataType)
      }
    }
    
    if (edge.active) {
      edgeWidth = 3
      edgeColor = '#8B5CF6'
    }
    
    return {
      id: edge.id,
      from: edge.source,
      to: edge.target,
      color: {
        color: edgeColor,
        highlight: '#8B5CF6',
        hover: '#9CA3AF',
        opacity: edge.active ? 1 : 0.8,
      },
      width: edgeWidth,
      arrows: {
        to: {
          enabled: true,
          scaleFactor: 0.8,
        },
      },
      smooth: {
        enabled: true,
        type: 'curvedCW',
        roundness: 0.3,
      },
      dashes: edge.active ? false : [8, 4],
      shadow: edge.active ? {
        enabled: true,
        color: 'rgba(139, 92, 246, 0.3)',
        size: 10,
        x: 0,
        y: 0,
      } : undefined,
      animation: edge.active ? {
        enabled: true,
        speed: 5,
        type: 'dash',
      } : undefined,
    }
  })
}

function getPortColorByType(dataType: string): string {
  const colors: Record<string, string> = {
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

function getVisOptions(): Options {
  return {
    physics: {
      enabled: false,
    },
    interaction: {
      dragNodes: !isExecuting.value,
      dragView: true,
      zoomView: true,
      selectable: true,
      hover: true,
    },
    manipulation: {
      enabled: false,
    },
    nodes: {
      borderWidthSelected: 3,
      chosen: true,
    },
    edges: {
      smooth: {
        enabled: true,
        type: 'curvedCW',
        roundness: 0.2,
      },
    },
  }
}

function initNetwork() {
  if (!networkContainer.value) return
  
  nodesDataSet.value = new DataSet<Node>(getVisNodes())
  edgesDataSet.value = new DataSet<Edge>(getVisEdges())
  
  const data: Data = {
    nodes: nodesDataSet.value,
    edges: edgesDataSet.value,
  }
  
  network.value = new Network(networkContainer.value, data, getVisOptions())
  
  network.value.on('click', (params: any) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      isUpdatingFromWatch.value = true
      selectNode(nodeId)
      emit('node-selected', nodeId)
      nextTick(() => { isUpdatingFromWatch.value = false })
    } else if (params.edges.length > 0) {
      const edgeId = params.edges[0]
      isUpdatingFromWatch.value = true
      selectEdge(edgeId)
      emit('edge-selected', edgeId)
      nextTick(() => { isUpdatingFromWatch.value = false })
    } else {
      isUpdatingFromWatch.value = true
      clearSelection()
      emit('canvas-click')
      nextTick(() => { isUpdatingFromWatch.value = false })
    }
  })
  
  network.value.on('dragEnd', (params: any) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const positions = network.value?.getPositions([nodeId])
      if (positions && positions[nodeId]) {
        isUpdatingFromWatch.value = true
        updateNodePosition(nodeId, {
          x: positions[nodeId].x,
          y: positions[nodeId].y,
        })
        nextTick(() => { isUpdatingFromWatch.value = false })
      }
    }
  })
  
  network.value.on('doubleClick', (params: any) => {
    if (params.nodes.length === 0 && params.edges.length === 0) {
      const canvasRect = networkContainer.value?.getBoundingClientRect()
      if (canvasRect) {
        const position = network.value?.canvasToDOM({
          x: params.pointer.canvas.x,
          y: params.pointer.canvas.y,
        })
        if (position) {
          addNode('agent', { x: position.x, y: position.y })
        }
      }
    }
  })
}

function updateNetwork() {
  if (!network.value || !nodesDataSet.value || !edgesDataSet.value) return
  
  if (isUpdatingFromWatch.value) return
  
  const currentNodes = nodesDataSet.value.getIds().map(String)
  const newNodes = getVisNodes()
  const newNodeIds = new Set(newNodes.map(n => String(n.id)))
  
  const nodesToAdd = newNodes.filter(n => !currentNodes.includes(String(n.id)))
  const nodesToUpdate = newNodes.filter(n => currentNodes.includes(String(n.id)))
  const nodeIdsToRemove = currentNodes.filter(id => !newNodeIds.has(id))
  
  const shouldFit = currentNodes.length === 0 && nodesToAdd.length > 0
  
  if (nodesToAdd.length > 0) {
    nodesDataSet.value.add(nodesToAdd)
  }
  if (nodesToUpdate.length > 0) {
    nodesDataSet.value.updateOnly(nodesToUpdate.map(n => ({ ...n, id: String(n.id) })))
  }
  if (nodeIdsToRemove.length > 0) {
    nodesDataSet.value.remove(nodeIdsToRemove)
  }
  
  const currentEdges = edgesDataSet.value.getIds().map(String)
  const newEdges = getVisEdges()
  const newEdgeIds = new Set(newEdges.map(e => String(e.id)))
  
  const edgesToAdd = newEdges.filter(e => !currentEdges.includes(String(e.id)))
  const edgesToUpdate = newEdges.filter(e => currentEdges.includes(String(e.id)))
  const edgeIdsToRemove = currentEdges.filter(id => !newEdgeIds.has(id))
  
  if (edgesToAdd.length > 0) {
    edgesDataSet.value.add(edgesToAdd)
  }
  if (edgesToUpdate.length > 0) {
    edgesDataSet.value.updateOnly(edgesToUpdate.map(e => ({ ...e, id: String(e.id) })))
  }
  if (edgeIdsToRemove.length > 0) {
    edgesDataSet.value.remove(edgeIdsToRemove)
  }
  
  if (shouldFit && nodesToAdd.length > 0) {
    setTimeout(() => {
      network.value?.fit({
        animation: {
          duration: 300,
          easingFunction: 'easeInOutQuad',
        },
      })
    }, 100)
  }
}

function zoomIn() {
  if (!network.value) return
  const scale = network.value.getScale() * 1.2
  network.value.moveTo({ scale })
  zoom.value = scale
}

function zoomOut() {
  if (!network.value) return
  const scale = network.value.getScale() / 1.2
  network.value.moveTo({ scale })
  zoom.value = scale
}

function resetView() {
  if (!network.value) return
  network.value.fit({
    animation: {
      duration: 500,
      easingFunction: 'easeInOutQuad',
    },
  })
  zoom.value = 1
}

function startConnection(nodeId: string) {
  isConnecting.value = true
  connectingFrom.value = nodeId
}

function completeConnection(targetId: string) {
  if (connectingFrom.value && connectingFrom.value !== targetId) {
    addEdge(connectingFrom.value, targetId)
  }
  cancelConnection()
}

function cancelConnection() {
  isConnecting.value = false
  connectingFrom.value = null
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  
  const nodeType = event.dataTransfer?.getData('nodeType') as WorkflowNodeType
  if (!nodeType || !network.value || !networkContainer.value) return
  
  const rect = networkContainer.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  const position = network.value.DOMtoCanvas({ x, y })
  addNode(nodeType, { x: position.x, y: position.y })
}

watch([nodes, edges], () => {
  nextTick(() => {
    updateNetwork()
  })
}, { deep: true })

watch(isExecuting, () => {
  if (network.value) {
    network.value.setOptions(getVisOptions())
  }
})

onMounted(() => {
  nextTick(() => {
    initNetwork()
  })
})

onUnmounted(() => {
  if (network.value) {
    network.value.destroy()
  }
})

defineExpose({
  zoomIn,
  zoomOut,
  resetView,
  startConnection,
  completeConnection,
  cancelConnection,
  handleDrop,
})
</script>

<style scoped>
.workflow-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  background: var(--bg-primary);
  border-radius: 8px;
  overflow: hidden;
}

.canvas-toolbar {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-secondary);
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  z-index: 10;
}

.zoom-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.zoom-btn:hover {
  background: var(--bg-tertiary);
  border-color: var(--text-muted);
}

.zoom-btn svg {
  width: 16px;
  height: 16px;
  color: var(--text-secondary);
}

.zoom-level {
  font-size: 0.85rem;
  color: var(--text-secondary);
  min-width: 40px;
  text-align: center;
}

.canvas-area {
  width: 100%;
  height: 100%;
}

.connection-indicator {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-secondary);
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid #8B5CF6;
  z-index: 10;
}

.connection-indicator span {
  color: var(--text-primary);
  font-size: 0.9rem;
}

.cancel-btn {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}
</style>
