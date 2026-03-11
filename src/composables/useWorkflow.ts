import { ref, computed } from 'vue'
import { useWorkflowStore } from '@/stores/workflow-store'
import type {
  Workflow,
  WorkflowNode,
  WorkflowEdge,
  WorkflowNodeType,
  NodeConfig,
  NodeStatus,
  WorkflowTemplate,
} from '@/types/workflow'
import { WORKFLOW_TEMPLATES } from '@/types/workflow'
import { workflowAPI, type NodeStatusEvent, type LogEvent } from '@/services/workflow'
import { workflowCache } from '@/utils/cache-manager'

export function useWorkflow() {
  const store = useWorkflowStore()
  
  const error = ref<string | null>(null)
  
  let progressUnsubscribe: (() => void) | null = null
  
  const nodes = computed(() => store.nodes)
  const edges = computed(() => store.edges)
  const selectedNodeId = computed(() => store.selectedNodeId)
  const selectedEdgeId = computed(() => store.selectedEdgeId)
  const isExecuting = computed(() => store.isExecuting)
  const executionProgress = computed(() => store.executionProgress)
  const canUndo = computed(() => store.canUndo)
  const canRedo = computed(() => store.canRedo)
  const currentWorkflow = computed(() => store.currentWorkflow)
  const executionLogs = computed(() => store.executionLogs)
  const executionOutput = computed(() => store.executionOutput)
  const currentSessionId = computed(() => store.currentSessionId)
  
  const selectedNode = computed(() => 
    selectedNodeId.value ? nodes.value.find(n => n.id === selectedNodeId.value) : null
  )
  
  const selectedEdge = computed(() =>
    selectedEdgeId.value ? edges.value.find(e => e.id === selectedEdgeId.value) : null
  )

  function saveHistory() {
    store.saveHistory()
  }

  function undo() {
    store.undo()
  }

  function redo() {
    store.redo()
  }

  function createNewWorkflow(name: string = 'Untitled Workflow') {
    store.createNewWorkflow(name)
    error.value = null
  }

  function loadWorkflow(workflow: Workflow) {
    store.loadWorkflow(workflow)
    error.value = null
  }

  function addNode(
    type: WorkflowNodeType,
    position: { x: number; y: number },
    config?: Partial<NodeConfig>
  ): WorkflowNode | null {
    error.value = null
    
    try {
      return store.addNode(type, position, config)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to add node'
      return null
    }
  }

  function updateNode(nodeId: string, updates: Partial<WorkflowNode>) {
    store.updateNode(nodeId, updates)
  }

  function updateNodeConfig(nodeId: string, config: Partial<NodeConfig>) {
    store.updateNodeConfig(nodeId, config)
  }

  function updateNodePosition(nodeId: string, position: { x: number; y: number }) {
    store.updateNodePosition(nodeId, position)
  }

  function updateNodeStatus(nodeId: string, status: NodeStatus) {
    store.updateNodeStatus(nodeId, status)
  }

  function deleteNode(nodeId: string) {
    store.deleteNode(nodeId)
  }

  function addEdge(
    source: string,
    target: string,
    sourcePort?: string,
    targetPort?: string
  ): WorkflowEdge | null {
    error.value = null
    
    const existingEdge = edges.value.find(
      e => e.source === source && e.target === target
    )
    if (existingEdge) {
      error.value = 'Edge already exists'
      return null
    }
    
    if (source === target) {
      error.value = 'Cannot connect node to itself'
      return null
    }
    
    const result = store.addEdge(source, target, sourcePort, targetPort)
    if (!result.success) {
      error.value = result.error || 'Failed to add edge'
      return null
    }
    
    return result.edge || null
  }

  function deleteEdge(edgeId: string) {
    store.deleteEdge(edgeId)
  }

  function selectNode(nodeId: string | null) {
    store.selectNode(nodeId)
  }

  function selectEdge(edgeId: string | null) {
    store.selectEdge(edgeId)
  }

  function clearSelection() {
    store.clearSelection()
  }

  function applyTemplate(templateId: string) {
    const template = WORKFLOW_TEMPLATES.find(t => t.id === templateId)
    if (!template) {
      error.value = 'Template not found'
      return
    }
    
    store.applyTemplate(templateId)
    error.value = null
  }

  function getTemplates(): WorkflowTemplate[] {
    return WORKFLOW_TEMPLATES
  }

  function validateWorkflow(): { valid: boolean; errors: string[] } {
    const errors: string[] = []
    
    if (nodes.value.length === 0) {
      errors.push('Workflow must have at least one node')
    }
    
    const inputNodes = nodes.value.filter(n => n.type === 'input')
    if (inputNodes.length === 0) {
      errors.push('Workflow must have at least one input node')
    }
    
    const outputNodes = nodes.value.filter(n => n.type === 'output')
    if (outputNodes.length === 0) {
      errors.push('Workflow must have at least one output node')
    }
    
    nodes.value.forEach(node => {
      if (node.type === 'agent' && !node.config.agentId) {
        errors.push(`Agent node "${node.label}" must have an agent selected`)
      }
      
      if (node.type === 'skill' && !node.config.skillId) {
        errors.push(`Skill node "${node.label}" must have a skill selected`)
      }
    })
    
    edges.value.forEach(edge => {
      const sourceNode = nodes.value.find(n => n.id === edge.source)
      const targetNode = nodes.value.find(n => n.id === edge.target)
      
      if (!sourceNode) {
        errors.push(`Edge references non-existent source node: ${edge.source}`)
      }
      if (!targetNode) {
        errors.push(`Edge references non-existent target node: ${edge.target}`)
      }
    })
    
    return {
      valid: errors.length === 0,
      errors,
    }
  }

  async function executeWorkflow(input?: { instruction: string; paperIds?: string[] }): Promise<boolean> {
    const validation = validateWorkflow()
    if (!validation.valid) {
      error.value = validation.errors.join('; ')
      return false
    }
    
    const workflow = store.exportWorkflow()
    const inputNode = nodes.value.find(n => n.type === 'input')
    const instruction = input?.instruction || inputNode?.config?.instruction || 'Execute workflow'
    
    store.setExecuting(true)
    store.setExecutionProgress(0)
    store.resetAllNodeStatus()
    store.clearExecutionLogs()
    store.setExecutionOutput(null)
    store.setCurrentSessionId(null)
    error.value = null
    
    try {
      progressUnsubscribe = workflowAPI.onProgress(handleProgressEvent)
      
      const response = await workflowAPI.execute(workflow, {
        instruction,
        paperIds: input?.paperIds || inputNode?.config?.paperIds,
      })
      
      store.setCurrentSessionId(response.session_id)
      
      workflowAPI.connectProgressStream(response.session_id)
      
      return new Promise((resolve) => {
        const checkCompletion = setInterval(() => {
          if (!store.isExecuting) {
            clearInterval(checkCompletion)
            resolve(!error.value)
          }
        }, 100)
      })
      
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Execution failed'
      store.setExecuting(false)
      cleanup()
      return false
    }
  }

  function handleProgressEvent(event: string, data: unknown): void {
    switch (event) {
      case 'node_status':
        handleNodeStatus(data as NodeStatusEvent)
        break
      case 'session_completed':
        handleSessionCompleted(data as { sessionId: string; output?: string; error?: string })
        break
      case 'log':
        handleLog(data as LogEvent)
        break
      case 'connected':
        addLog('info', 'Connected to execution stream')
        break
      case 'heartbeat':
        break
    }
  }

  function handleNodeStatus(data: NodeStatusEvent): void {
    const status: NodeStatus = data.status as NodeStatus
    store.updateNodeStatus(data.nodeId, status)
    
    if (data.result !== undefined) {
      store.updateNode(data.nodeId, { result: data.result })
      
      const node = nodes.value.find(n => n.id === data.nodeId)
      if (node && status === 'success') {
        workflowCache.set(node, [], data.result)
      }
    }
    if (data.error) {
      store.updateNode(data.nodeId, { error: data.error })
    }
    
    const totalNodes = nodes.value.length
    const completedNodes = nodes.value.filter(n => n.status === 'success' || n.status === 'error').length
    store.setExecutionProgress((completedNodes / totalNodes) * 100)
    
    addLog('info', `Node ${data.nodeId} status: ${data.status}`, data.nodeId)
  }

  function handleSessionCompleted(data: { sessionId: string; output?: string; error?: string }): void {
    if (data.output) {
      store.setExecutionOutput(data.output)
    }
    if (data.error) {
      error.value = data.error
    }
    
    store.setExecuting(false)
    store.setExecutionProgress(100)
    store.addExecutionLog('info', data.error ? `Session failed: ${data.error}` : 'Session completed successfully')
    
    cleanup()
  }

  function handleLog(data: LogEvent): void {
    store.addExecutionLog(data.level, data.message, data.nodeId)
  }

  function addLog(level: string, message: string, nodeId?: string): void {
    store.addExecutionLog(level, message, nodeId)
  }

  function cleanup(): void {
    if (progressUnsubscribe) {
      progressUnsubscribe()
      progressUnsubscribe = null
    }
    workflowAPI.disconnect()
  }

  function stopExecution() {
    if (currentSessionId.value) {
      workflowAPI.cancel(currentSessionId.value)
    }
    cleanup()
    store.setExecuting(false)
    store.resetAllNodeStatus()
  }

  function exportToJSON(): string {
    const workflow = store.exportWorkflow()
    return JSON.stringify(workflow, null, 2)
  }

  function importFromJSON(json: string): boolean {
    try {
      const workflow = JSON.parse(json) as Workflow
      store.loadWorkflow(workflow)
      return true
    } catch (e) {
      error.value = 'Invalid workflow JSON'
      return false
    }
  }

  async function getAvailableAgents(): Promise<string[]> {
    try {
      const response = await fetch('/api/team/stats')
      const data = await response.json()
      return data.available_agents || []
    } catch (e) {
      return ['research-agent', 'analysis-agent', 'writer-agent']
    }
  }

  async function getAvailableSkills(): Promise<string[]> {
    try {
      const response = await fetch('/api/skills')
      const data = await response.json()
      return data.skills?.map((s: any) => s.id) || []
    } catch (e) {
      return ['summary', 'translation', 'citation', 'related-papers']
    }
  }

  return {
    nodes,
    edges,
    selectedNodeId,
    selectedEdgeId,
    selectedNode,
    selectedEdge,
    isExecuting,
    executionProgress,
    canUndo,
    canRedo,
    currentWorkflow,
    error,
    currentSessionId,
    executionOutput,
    executionLogs,
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
    getTemplates,
    validateWorkflow,
    executeWorkflow,
    stopExecution,
    exportToJSON,
    importFromJSON,
    getAvailableAgents,
    getAvailableSkills,
    clearExecutionLogs: () => store.clearExecutionLogs(),
    clearCache: () => workflowCache.invalidateAll(),
    getCacheStats: () => workflowCache.getStats(),
  }
}
