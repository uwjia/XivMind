import type { WorkflowNode, NodeConfig } from '@/types/workflow'

interface CacheEntry {
  nodeId: string
  inputHash: string
  output: any
  timestamp: Date
  config: NodeConfig
}

const CACHE_KEY = 'xivmind_workflow_cache'
const MAX_CACHE_AGE = 24 * 60 * 60 * 1000

function generateInputHash(inputs: any[]): string {
  const json = JSON.stringify(inputs)
  let hash = 0
  for (let i = 0; i < json.length; i++) {
    const char = json.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return hash.toString(16)
}

function generateConfigHash(config: NodeConfig): string {
  const json = JSON.stringify(config)
  let hash = 0
  for (let i = 0; i < json.length; i++) {
    const char = json.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return hash.toString(16)
}

function loadCache(): Map<string, CacheEntry> {
  try {
    const stored = localStorage.getItem(CACHE_KEY)
    if (!stored) return new Map()
    
    const parsed = JSON.parse(stored) as CacheEntry[]
    const cache = new Map<string, CacheEntry>()
    const now = Date.now()
    
    for (const entry of parsed) {
      const age = now - new Date(entry.timestamp).getTime()
      if (age < MAX_CACHE_AGE) {
        cache.set(entry.nodeId, entry)
      }
    }
    
    return cache
  } catch {
    return new Map()
  }
}

function saveCache(cache: Map<string, CacheEntry>): void {
  try {
    const entries = Array.from(cache.values())
    localStorage.setItem(CACHE_KEY, JSON.stringify(entries))
  } catch (e) {
    console.warn('Failed to save workflow cache:', e)
  }
}

class WorkflowCache {
  private cache: Map<string, CacheEntry>
  
  constructor() {
    this.cache = loadCache()
  }
  
  get(
    node: WorkflowNode,
    inputs: any[]
  ): { hit: boolean; output?: any } {
    const entry = this.cache.get(node.id)
    if (!entry) {
      return { hit: false }
    }
    
    const inputHash = generateInputHash(inputs)
    const configHash = generateConfigHash(node.config)
    const combinedHash = `${inputHash}_${configHash}`
    
    if (entry.inputHash === combinedHash) {
      return { hit: true, output: entry.output }
    }
    
    return { hit: false }
  }
  
  set(
    node: WorkflowNode,
    inputs: any[],
    output: any
  ): void {
    const inputHash = generateInputHash(inputs)
    const configHash = generateConfigHash(node.config)
    const combinedHash = `${inputHash}_${configHash}`
    
    const entry: CacheEntry = {
      nodeId: node.id,
      inputHash: combinedHash,
      output,
      timestamp: new Date(),
      config: { ...node.config },
    }
    
    this.cache.set(node.id, entry)
    saveCache(this.cache)
  }
  
  invalidate(nodeId: string): void {
    this.cache.delete(nodeId)
    saveCache(this.cache)
  }
  
  invalidateAll(): void {
    this.cache.clear()
    saveCache(this.cache)
  }
  
  getStats(): { size: number; entries: Array<{ nodeId: string; timestamp: Date }> } {
    return {
      size: this.cache.size,
      entries: Array.from(this.cache.values()).map(e => ({
        nodeId: e.nodeId,
        timestamp: e.timestamp,
      })),
    }
  }
}

export const workflowCache = new WorkflowCache()

export function needsReexecution(
  node: WorkflowNode,
  inputs: any[],
  cachedNodes: Set<string>
): boolean {
  if (node.status === 'error') return true
  if (!cachedNodes.has(node.id)) return true
  
  const { hit } = workflowCache.get(node, inputs)
  return !hit
}

export function getExecutionPlan(
  nodes: WorkflowNode[],
  edges: Array<{ source: string; target: string }>,
  changedNodes: Set<string>
): string[][] {
  const inDegree = new Map(nodes.map(n => [n.id, 0]))
  const adjacency = new Map(nodes.map(n => [n.id, [] as string[]]))
  
  for (const edge of edges) {
    const sourceList = adjacency.get(edge.source)
    if (sourceList) {
      sourceList.push(edge.target)
    }
    const targetDegree = inDegree.get(edge.target)
    if (targetDegree !== undefined) {
      inDegree.set(edge.target, targetDegree + 1)
    }
  }
  
  const affectedNodes = new Set<string>(changedNodes)
  const queue = [...changedNodes]
  
  while (queue.length > 0) {
    const nodeId = queue.shift()!
    const successors = adjacency.get(nodeId) || []
    for (const successorId of successors) {
      if (!affectedNodes.has(successorId)) {
        affectedNodes.add(successorId)
        queue.push(successorId)
      }
    }
  }
  
  const levels: string[][] = []
  const remaining = new Set(nodes.map(n => n.id))
  
  while (remaining.size > 0) {
    const level: string[] = []
    
    for (const nodeId of remaining) {
      const degree = inDegree.get(nodeId) || 0
      if (degree === 0) {
        level.push(nodeId)
      }
    }
    
    if (level.length === 0) {
      break
    }
    
    const filteredLevel = level.filter(id => affectedNodes.has(id))
    if (filteredLevel.length > 0) {
      levels.push(filteredLevel)
    }
    
    for (const nodeId of level) {
      remaining.delete(nodeId)
      const successors = adjacency.get(nodeId) || []
      for (const successorId of successors) {
        const currentDegree = inDegree.get(successorId) || 0
        inDegree.set(successorId, currentDegree - 1)
      }
    }
  }
  
  return levels
}
