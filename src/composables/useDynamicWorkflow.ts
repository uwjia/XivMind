import { ref, computed, onUnmounted } from 'vue'
import { useWorkflowStore } from '@/stores/workflow-store'
import { workflowAPI } from '@/services/workflow'
import type {
  Workflow,
  DynamicNodeConfig,
  DynamicWorkflowPhase,
  SubtasksCreatedEvent,
  DynamicNodeCreatedEvent,
  DynamicEdgeCreatedEvent,
  ExecutionPhaseEvent,
  NodeStatusEvent,
  SessionCompletedEvent,
  LogEvent,
} from '@/types/workflow'

export function useDynamicWorkflow() {
  const store = useWorkflowStore()
  
  const isExecuting = ref(false)
  const error = ref<string | null>(null)
  const progressUnsubscribe = ref<(() => void) | null>(null)
  
  const phase = computed(() => store.dynamicPhase)
  const phaseMessage = computed(() => store.dynamicPhaseMessage)
  const subtasks = computed(() => store.subtasks)
  const dynamicNodeIds = computed(() => store.dynamicNodeIds)
  const agentResults = computed(() => store.agentResults)
  
  async function executeDynamicWorkflow(
    workflow: Workflow,
    input: { instruction: string; paperIds?: string[] }
  ): Promise<boolean> {
    error.value = null
    isExecuting.value = true
    
    store.setDynamicMode(true)
    store.setDynamicPhase('initializing', 'Starting dynamic workflow...')
    store.setExecuting(true)
    store.resetAllNodeStatus()
    store.clearExecutionLogs()
    store.clearDynamicState()
    
    try {
      progressUnsubscribe.value = workflowAPI.onProgress(handleProgressEvent)
      
      const response = await workflowAPI.executeDynamic(workflow, input)
      
      store.setCurrentSessionId(response.session_id)
      
      workflowAPI.connectProgressStream(response.session_id)
      
      return new Promise((resolve) => {
        const checkCompletion = setInterval(() => {
          if (!isExecuting.value) {
            clearInterval(checkCompletion)
            resolve(!error.value)
          }
        }, 100)
      })
      
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Dynamic execution failed'
      isExecuting.value = false
      store.setExecuting(false)
      store.setDynamicPhase('error', error.value)
      cleanup()
      return false
    }
  }
  
  function handleProgressEvent(event: string, data: unknown): void {
    switch (event) {
      case 'connected':
        store.addExecutionLog('info', 'Connected to execution stream')
        break
        
      case 'execution_phase':
        handleExecutionPhase(data as ExecutionPhaseEvent)
        break
        
      case 'subtasks_created':
        handleSubtasksCreated(data as SubtasksCreatedEvent)
        break
        
      case 'dynamic_node_created':
        handleDynamicNodeCreated(data as DynamicNodeCreatedEvent)
        break
        
      case 'dynamic_edge_created':
        handleDynamicEdgeCreated(data as DynamicEdgeCreatedEvent)
        break
        
      case 'node_status':
        handleNodeStatus(data as NodeStatusEvent)
        break
        
      case 'session_completed':
        handleSessionCompleted(data as SessionCompletedEvent)
        break
        
      case 'log':
        handleLog(data as LogEvent)
        break
        
      case 'heartbeat':
        break
    }
  }
  
  function handleExecutionPhase(data: ExecutionPhaseEvent): void {
    store.setDynamicPhase(data.phase as DynamicWorkflowPhase, data.message)
    store.addExecutionLog('info', `[Phase] ${data.phase}: ${data.message}`)
  }
  
  function handleSubtasksCreated(data: SubtasksCreatedEvent): void {
    store.setSubtasks(data.subtasks)
    store.addExecutionLog('info', `Received ${data.subtasks.length} subtasks from analysis`)
  }
  
  function handleDynamicNodeCreated(data: DynamicNodeCreatedEvent): void {
    const config: DynamicNodeConfig = {
      nodeId: data.nodeId,
      nodeType: data.nodeType as 'agent' | 'synthesize' | 'output',
      label: data.label,
      config: data.config,
      position: data.position,
      sourceNodeIds: data.sourceNodeIds,
    }
    
    store.addDynamicNode(config)
    store.addExecutionLog('info', `Created dynamic node: ${data.label} (${data.nodeType})`)
    
    if (data.sourceNodeIds && data.sourceNodeIds.length > 0) {
      for (const sourceId of data.sourceNodeIds) {
        const edge = store.addDynamicEdge(sourceId, data.nodeId)
        if (edge) {
          store.addExecutionLog('info', `Created dynamic edge: ${sourceId} -> ${data.nodeId}`)
        }
      }
    }
  }
  
  function handleDynamicEdgeCreated(data: DynamicEdgeCreatedEvent): void {
    const edge = store.addDynamicEdge(data.source, data.target)
    if (edge) {
      store.addExecutionLog('info', `Created dynamic edge: ${data.source} -> ${data.target}`)
    }
  }
  
  function handleNodeStatus(data: NodeStatusEvent): void {
    store.updateNodeStatus(data.nodeId, data.status)
    
    if (data.result !== undefined) {
      store.updateNode(data.nodeId, { result: data.result })
      store.setAgentResult(data.nodeId, data.result)
    }
    
    if (data.error) {
      store.updateNode(data.nodeId, { error: data.error })
    }
    
    const totalNodes = store.nodes.length
    const completedNodes = store.nodes.filter(
      n => n.status === 'success' || n.status === 'error'
    ).length
    store.setExecutionProgress((completedNodes / totalNodes) * 100)
  }
  
  function handleSessionCompleted(data: SessionCompletedEvent): void {
    isExecuting.value = false
    store.setExecuting(false)
    store.setDynamicPhase('completed', 'Workflow completed')
    
    if (data.output) {
      store.setExecutionOutput(data.output)
      store.addExecutionLog('info', 'Workflow completed successfully')
    }
    
    if (data.error) {
      error.value = data.error
      store.setDynamicPhase('error', data.error)
      store.addExecutionLog('error', `Workflow failed: ${data.error}`)
    }
    
    cleanup()
  }
  
  function handleLog(data: LogEvent): void {
    store.addExecutionLog(data.level, data.message, data.nodeId)
  }
  
  async function cancelExecution(): Promise<void> {
    const sessionId = store.currentSessionId
    if (!sessionId) return
    
    try {
      await workflowAPI.cancelDynamic(sessionId)
      store.addExecutionLog('info', 'Workflow cancelled by user')
    } catch (e) {
      store.addExecutionLog('error', `Cancel failed: ${e}`)
    }
    
    isExecuting.value = false
    store.setExecuting(false)
    store.setDynamicPhase('idle', '')
    cleanup()
  }
  
  function cleanup(): void {
    if (progressUnsubscribe.value) {
      progressUnsubscribe.value()
      progressUnsubscribe.value = null
    }
    workflowAPI.disconnect()
  }
  
  function resetDynamicState(): void {
    store.clearDynamicState()
    store.setDynamicMode(false)
    error.value = null
    isExecuting.value = false
  }
  
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    isExecuting,
    error,
    phase,
    phaseMessage,
    subtasks,
    dynamicNodeIds,
    agentResults,
    executeDynamicWorkflow,
    cancelExecution,
    resetDynamicState,
  }
}
