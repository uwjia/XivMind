import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Workflow,
  WorkflowNode,
  WorkflowEdge,
  WorkflowNodeType,
  NodeStatus,
  NodeConfig,
} from '@/types/workflow'
import { createNode, createEdge, WORKFLOW_TEMPLATES, areTypesCompatible } from '@/types/workflow'

export interface ConnectionError {
  message: string
  sourceNodeId?: string
  targetNodeId?: string
}

export const useWorkflowStore = defineStore('workflow', () => {
  const currentWorkflow = ref<Workflow | null>(null)
  const nodes = ref<WorkflowNode[]>([])
  const edges = ref<WorkflowEdge[]>([])
  const selectedNodeId = ref<string | null>(null)
  const selectedEdgeId = ref<string | null>(null)
  const isExecuting = ref(false)
  const executionProgress = ref(0)
  const history = ref<Workflow[][]>([])
  const historyIndex = ref(-1)
  const zoom = ref(1)
  const pan = ref({ x: 0, y: 0 })
  const executionLogs = ref<Array<{ timestamp: Date; level: string; message: string; nodeId?: string }>>([])
  const executionOutput = ref<string | null>(null)
  const currentSessionId = ref<string | null>(null)

  const selectedNode = computed(() => {
    if (!selectedNodeId.value) return null
    return nodes.value.find(n => n.id === selectedNodeId.value) || null
  })

  const selectedEdge = computed(() => {
    if (!selectedEdgeId.value) return null
    return edges.value.find(e => e.id === selectedEdgeId.value) || null
  })

  const nodeCount = computed(() => nodes.value.length)
  const edgeCount = computed(() => edges.value.length)

  const canUndo = computed(() => historyIndex.value > 0)
  const canRedo = computed(() => historyIndex.value < history.value.length - 1)

  const runningNodes = computed(() => 
    nodes.value.filter(n => n.status === 'running')
  )

  const completedNodes = computed(() => 
    nodes.value.filter(n => n.status === 'success')
  )

  const failedNodes = computed(() => 
    nodes.value.filter(n => n.status === 'error')
  )

  function saveHistory() {
    const state = [
      [...nodes.value],
      [...edges.value],
    ]
    
    if (historyIndex.value < history.value.length - 1) {
      history.value = history.value.slice(0, historyIndex.value + 1)
    }
    
    history.value.push(state as any)
    historyIndex.value = history.value.length - 1
    
    if (history.value.length > 50) {
      history.value.shift()
      historyIndex.value--
    }
  }

  function undo() {
    if (!canUndo.value) return
    
    historyIndex.value--
    const state = history.value[historyIndex.value]
    if (state) {
      nodes.value = JSON.parse(JSON.stringify(state[0]))
      edges.value = JSON.parse(JSON.stringify(state[1]))
    }
  }

  function redo() {
    if (!canRedo.value) return
    
    historyIndex.value++
    const state = history.value[historyIndex.value]
    if (state) {
      nodes.value = JSON.parse(JSON.stringify(state[0]))
      edges.value = JSON.parse(JSON.stringify(state[1]))
    }
  }

  function createNewWorkflow(name: string = 'Untitled Workflow') {
    saveHistory()
    
    currentWorkflow.value = {
      id: `workflow_${Date.now()}`,
      name,
      description: '',
      nodes: [],
      edges: [],
      variables: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    
    nodes.value = []
    edges.value = []
    selectedNodeId.value = null
    selectedEdgeId.value = null
  }

  function loadWorkflow(workflow: Workflow) {
    saveHistory()
    
    currentWorkflow.value = workflow
    nodes.value = [...workflow.nodes]
    edges.value = [...workflow.edges]
    selectedNodeId.value = null
    selectedEdgeId.value = null
  }

  function addNode(
    type: WorkflowNodeType,
    position: { x: number; y: number },
    config?: Partial<NodeConfig>
  ) {
    saveHistory()
    
    const node = createNode(type, position, config)
    nodes.value.push(node)
    
    updateNodeConnections(node.id)
    
    return node
  }

  function updateNode(nodeId: string, updates: Partial<WorkflowNode>) {
    const index = nodes.value.findIndex(n => n.id === nodeId)
    if (index === -1) return
    
    saveHistory()
    nodes.value[index] = { ...nodes.value[index], ...updates }
  }

  function updateNodeConfig(nodeId: string, config: Partial<NodeConfig>) {
    const node = nodes.value.find(n => n.id === nodeId)
    if (!node) return
    
    saveHistory()
    node.config = { ...node.config, ...config }
  }

  function updateNodePosition(nodeId: string, position: { x: number; y: number }) {
    const node = nodes.value.find(n => n.id === nodeId)
    if (!node) return
    
    node.position = position
  }

  function updateNodeStatus(nodeId: string, status: NodeStatus) {
    const node = nodes.value.find(n => n.id === nodeId)
    if (!node) return
    
    node.status = status
  }

  function deleteNode(nodeId: string) {
    const index = nodes.value.findIndex(n => n.id === nodeId)
    if (index === -1) return
    
    saveHistory()
    
    edges.value = edges.value.filter(
      e => e.source !== nodeId && e.target !== nodeId
    )
    
    nodes.value.splice(index, 1)
    
    if (selectedNodeId.value === nodeId) {
      selectedNodeId.value = null
    }
  }

  function addEdge(
    source: string,
    target: string,
    sourcePort?: string,
    targetPort?: string
  ): { success: boolean; edge?: WorkflowEdge; error?: string } {
    const sourceNode = nodes.value.find(n => n.id === source)
    const targetNode = nodes.value.find(n => n.id === target)
    
    if (!sourceNode) {
      return { success: false, error: 'Source node not found' }
    }
    if (!targetNode) {
      return { success: false, error: 'Target node not found' }
    }
    
    const sourcePortObj = sourcePort 
      ? sourceNode.outputs.find(p => p.id === sourcePort)
      : sourceNode.outputs[0]
    
    const targetPortObj = targetPort
      ? targetNode.inputs.find(p => p.id === targetPort)
      : targetNode.inputs[0]
    
    if (!sourcePortObj) {
      return { success: false, error: 'Source port not found' }
    }
    if (!targetPortObj) {
      return { success: false, error: 'Target port not found' }
    }
    
    if (!areTypesCompatible(sourcePortObj.dataType, targetPortObj.dataType)) {
      return { 
        success: false, 
        error: `Type mismatch: cannot connect ${sourcePortObj.dataType} to ${targetPortObj.dataType}` 
      }
    }
    
    const existingEdge = edges.value.find(
      e => e.source === source && e.target === target
    )
    if (existingEdge) {
      return { success: false, error: 'Edge already exists' }
    }
    
    saveHistory()
    
    const edge = createEdge(source, target, sourcePortObj.id, targetPortObj.id)
    edges.value.push(edge)
    
    updateNodeConnections(source)
    updateNodeConnections(target)
    
    return { success: true, edge }
  }

  function deleteEdge(edgeId: string) {
    const index = edges.value.findIndex(e => e.id === edgeId)
    if (index === -1) return
    
    const edge = edges.value[index]
    
    saveHistory()
    
    edges.value.splice(index, 1)
    
    updateNodeConnections(edge.source)
    updateNodeConnections(edge.target)
    
    if (selectedEdgeId.value === edgeId) {
      selectedEdgeId.value = null
    }
  }

  function updateNodeConnections(nodeId: string) {
    const node = nodes.value.find(n => n.id === nodeId)
    if (!node) return
    
    node.inputs.forEach(port => {
      port.connected = edges.value.some(e => e.target === nodeId)
    })
    
    node.outputs.forEach(port => {
      port.connected = edges.value.some(e => e.source === nodeId)
    })
  }

  function selectNode(nodeId: string | null) {
    selectedNodeId.value = nodeId
    selectedEdgeId.value = null
  }

  function selectEdge(edgeId: string | null) {
    selectedEdgeId.value = edgeId
    selectedNodeId.value = null
  }

  function clearSelection() {
    selectedNodeId.value = null
    selectedEdgeId.value = null
  }

  function applyTemplate(templateId: string) {
    const template = WORKFLOW_TEMPLATES.find(t => t.id === templateId)
    if (!template) return
    
    saveHistory()
    
    const labelToIdMap = new Map<string, string>()
    
    nodes.value = template.nodes.map((templateNode) => {
      const node = createNode(
        templateNode.type,
        templateNode.position,
        templateNode.config
      )
      node.label = templateNode.label
      labelToIdMap.set(templateNode.label, node.id)
      return node
    })
    
    edges.value = template.edges.map(templateEdge => {
      const sourceId = labelToIdMap.get(templateEdge.source)
      const targetId = labelToIdMap.get(templateEdge.target)
      
      if (sourceId && targetId) {
        return createEdge(sourceId, targetId)
      }
      return null
    }).filter((edge): edge is NonNullable<typeof edge> => edge !== null)
    
    if (currentWorkflow.value) {
      currentWorkflow.value.name = template.name
    }
  }

  function setZoom(newZoom: number) {
    zoom.value = Math.max(0.25, Math.min(2, newZoom))
  }

  function setPan(newPan: { x: number; y: number }) {
    pan.value = newPan
  }

  function setExecuting(value: boolean) {
    isExecuting.value = value
  }

  function setExecutionProgress(value: number) {
    executionProgress.value = value
  }

  function resetAllNodeStatus() {
    nodes.value.forEach(node => {
      node.status = 'idle'
    })
    edges.value.forEach(edge => {
      edge.active = false
    })
  }

  function addExecutionLog(level: string, message: string, nodeId?: string) {
    executionLogs.value.push({
      timestamp: new Date(),
      level,
      message,
      nodeId,
    })
  }

  function clearExecutionLogs() {
    executionLogs.value = []
  }

  function setExecutionOutput(output: string | null) {
    executionOutput.value = output
  }

  function setCurrentSessionId(sessionId: string | null) {
    currentSessionId.value = sessionId
  }

  function exportWorkflow(): Workflow {
    return {
      id: currentWorkflow.value?.id || `workflow_${Date.now()}`,
      name: currentWorkflow.value?.name || 'Untitled Workflow',
      description: currentWorkflow.value?.description || '',
      nodes: [...nodes.value],
      edges: [...edges.value],
      variables: currentWorkflow.value?.variables || [],
      createdAt: currentWorkflow.value?.createdAt || new Date(),
      updatedAt: new Date(),
    }
  }

  function $reset() {
    currentWorkflow.value = null
    nodes.value = []
    edges.value = []
    selectedNodeId.value = null
    selectedEdgeId.value = null
    isExecuting.value = false
    executionProgress.value = 0
    history.value = []
    historyIndex.value = -1
    zoom.value = 1
    pan.value = { x: 0, y: 0 }
    executionLogs.value = []
    executionOutput.value = null
    currentSessionId.value = null
  }

  return {
    currentWorkflow,
    nodes,
    edges,
    selectedNodeId,
    selectedEdgeId,
    isExecuting,
    executionProgress,
    zoom,
    pan,
    executionLogs,
    executionOutput,
    currentSessionId,
    selectedNode,
    selectedEdge,
    nodeCount,
    edgeCount,
    canUndo,
    canRedo,
    runningNodes,
    completedNodes,
    failedNodes,
    saveHistory,
    undo,
    redo,
    createNewWorkflow,
    loadWorkflow,
    addNode,
    updateNode,
    updateNodeConfig,
    updateNodePosition,
    updateNodeStatus,
    deleteNode,
    addEdge,
    deleteEdge,
    selectNode,
    selectEdge,
    clearSelection,
    applyTemplate,
    setZoom,
    setPan,
    setExecuting,
    setExecutionProgress,
    resetAllNodeStatus,
    addExecutionLog,
    clearExecutionLogs,
    setExecutionOutput,
    setCurrentSessionId,
    exportWorkflow,
    $reset,
  }
})
