import type { PortDataType, WorkflowNode, WorkflowEdge } from '@/types/workflow'
import { areTypesCompatible } from '@/types/workflow'

export function canConnectPorts(
  sourceNode: WorkflowNode,
  sourcePortId: string,
  targetNode: WorkflowNode,
  targetPortId: string
): { valid: boolean; reason?: string } {
  if (sourceNode.id === targetNode.id) {
    return { valid: false, reason: 'Cannot connect node to itself' }
  }
  
  const sourcePort = sourceNode.outputs.find(p => p.id === sourcePortId)
  const targetPort = targetNode.inputs.find(p => p.id === targetPortId)
  
  if (!sourcePort) {
    return { valid: false, reason: 'Source port not found' }
  }
  
  if (!targetPort) {
    return { valid: false, reason: 'Target port not found' }
  }
  
  if (sourcePort.connected && sourcePort.connectedTo !== targetPortId) {
    return { valid: false, reason: 'Source port already connected' }
  }
  
  if (targetPort.connected && targetPort.connectedTo !== sourcePortId) {
    return { valid: false, reason: 'Target port already connected' }
  }
  
  if (!areTypesCompatible(sourcePort.dataType, targetPort.dataType)) {
    return { 
      valid: false, 
      reason: `Type mismatch: ${sourcePort.dataType} -> ${targetPort.dataType}` 
    }
  }
  
  return { valid: true }
}

export function findEdgeByPort(
  edges: WorkflowEdge[],
  portId: string,
  isSource: boolean
): WorkflowEdge | undefined {
  return edges.find(edge => 
    isSource ? edge.sourcePort === portId : edge.targetPort === portId
  )
}

export function getPortColor(dataType: PortDataType): string {
  const colors: Record<PortDataType, string> = {
    text: '#3B82F6',
    data: '#8B5CF6',
    paper: '#10B981',
    analysis: '#F59E0B',
    task: '#EC4899',
    result: '#14B8A6',
    any: '#64748B',
  }
  return colors[dataType] || colors.any
}

export function getPortPosition(
  node: WorkflowNode,
  portId: string,
  nodeElement: HTMLElement
): { x: number; y: number } | null {
  const portElement = nodeElement.querySelector(`[data-port-id="${portId}"]`)
  if (!portElement) return null
  
  const nodeRect = nodeElement.getBoundingClientRect()
  const portRect = portElement.getBoundingClientRect()
  
  return {
    x: node.position.x + (portRect.left - nodeRect.left) + portRect.width / 2,
    y: node.position.y + (portRect.top - nodeRect.top) + portRect.height / 2,
  }
}

export function findPortAtPosition(
  nodes: WorkflowNode[],
  position: { x: number },
  nodeElements: Map<string, HTMLElement>,
  tolerance: number = 20
): { nodeId: string; portId: string; isOutput: boolean } | null {
  for (const node of nodes) {
    const element = nodeElements.get(node.id)
    if (!element) continue
    
    for (const port of node.outputs) {
      const portEl = element.querySelector(`[data-port-id="${port.id}"]`) as HTMLElement
      if (portEl) {
        const rect = portEl.getBoundingClientRect()
        if (Math.abs(position.x - rect.left) < tolerance) {
          return { nodeId: node.id, portId: port.id, isOutput: true }
        }
      }
    }
    
    for (const port of node.inputs) {
      const portEl = element.querySelector(`[data-port-id="${port.id}"]`) as HTMLElement
      if (portEl) {
        const rect = portEl.getBoundingClientRect()
        if (Math.abs(position.x - rect.left) < tolerance) {
          return { nodeId: node.id, portId: port.id, isOutput: false }
        }
      }
    }
  }
  
  return null
}
