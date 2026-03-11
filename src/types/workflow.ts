export type WorkflowNodeType =
  | 'input'
  | 'analyze'
  | 'decompose'
  | 'agent'
  | 'condition'
  | 'parallel'
  | 'synthesize'
  | 'output'
  | 'tool'
  | 'skill'

export type NodeStatus = 'idle' | 'pending' | 'running' | 'success' | 'error'

export type PortDataType =
  | 'text'
  | 'data'
  | 'paper'
  | 'analysis'
  | 'task'
  | 'result'
  | 'any'

export const TYPE_COMPATIBILITY: Record<PortDataType, PortDataType[]> = {
  text: ['text', 'any'],
  data: ['data', 'any'],
  paper: ['paper', 'data', 'any'],
  analysis: ['analysis', 'data', 'any'],
  task: ['task', 'data', 'any'],
  result: ['result', 'data', 'any'],
  any: ['text', 'data', 'paper', 'analysis', 'task', 'result', 'any'],
}

export function areTypesCompatible(sourceType: PortDataType, targetType: PortDataType): boolean {
  return TYPE_COMPATIBILITY[sourceType]?.includes(targetType) ?? false
}

export interface Port {
  id: string
  type: 'input' | 'output'
  label: string
  dataType: PortDataType
  required: boolean
  connected: boolean
  connectedTo?: string
}

export interface PortDefinition {
  label: string
  dataType: PortDataType
  required?: boolean
}

export interface NodeConfigField {
  key: string
  label: string
  type: 'text' | 'textarea' | 'select' | 'number' | 'checkbox'
  options?: string[]
  min?: number
  max?: number
  placeholder?: string
  defaultValue?: any
}

export interface NodeTypePortDefinition {
  inputs: PortDefinition[]
  outputs: PortDefinition[]
  configFields?: NodeConfigField[]
}

export const NODE_PORT_DEFINITIONS: Record<WorkflowNodeType, NodeTypePortDefinition> = {
  input: {
    inputs: [],
    outputs: [{ label: 'Output', dataType: 'text' }],
    configFields: [
      { key: 'instruction', label: 'Instruction', type: 'textarea', placeholder: 'Enter your task instruction...' },
      { key: 'paperIds', label: 'Paper IDs', type: 'text', placeholder: 'e.g., 2401.12345, 2401.67890' },
    ],
  },
  analyze: {
    inputs: [{ label: 'Input', dataType: 'text', required: true }],
    outputs: [
      { label: 'Analysis', dataType: 'analysis' },
      { label: 'Metadata', dataType: 'data' },
    ],
    configFields: [
      { key: 'timeout', label: 'Timeout (s)', type: 'number', min: 10, max: 600, defaultValue: 60 },
    ],
  },
  decompose: {
    inputs: [{ label: 'Input', dataType: 'text', required: true }],
    outputs: [{ label: 'Tasks', dataType: 'task' }],
    configFields: [
      { key: 'maxTasks', label: 'Max Tasks', type: 'number', min: 1, max: 10, defaultValue: 5 },
    ],
  },
  agent: {
    inputs: [{ label: 'Input', dataType: 'text', required: true }],
    outputs: [{ label: 'Result', dataType: 'result' }],
    configFields: [
      { key: 'agentId', label: 'Agent', type: 'select', options: [], placeholder: 'Select an agent...' },
      { key: 'instruction', label: 'Instruction', type: 'textarea', placeholder: 'Optional: Override workflow instruction...' },
    ],
  },
  condition: {
    inputs: [{ label: 'Input', dataType: 'data', required: true }],
    outputs: [
      { label: 'True', dataType: 'data' },
      { label: 'False', dataType: 'data' },
    ],
    configFields: [
      { key: 'condition', label: 'Condition', type: 'textarea', placeholder: 'e.g., complexity == "high"' },
    ],
  },
  parallel: {
    inputs: [{ label: 'Input', dataType: 'data', required: true }],
    outputs: [
      { label: 'Branch 1', dataType: 'data' },
      { label: 'Branch 2', dataType: 'data' },
      { label: 'Branch 3', dataType: 'data' },
    ],
    configFields: [
      { key: 'branches', label: 'Branches', type: 'number', min: 2, max: 5, defaultValue: 3 },
    ],
  },
  synthesize: {
    inputs: [
      { label: 'Input 1', dataType: 'data', required: true },
      { label: 'Input 2', dataType: 'data' },
      { label: 'Input 3', dataType: 'data' },
    ],
    outputs: [{ label: 'Result', dataType: 'result' }],
    configFields: [
      { key: 'strategy', label: 'Strategy', type: 'select', options: ['merge', 'summarize', 'vote'], defaultValue: 'merge' },
    ],
  },
  output: {
    inputs: [{ label: 'Input', dataType: 'data', required: true }],
    outputs: [],
  },
  tool: {
    inputs: [{ label: 'Input', dataType: 'data', required: true }],
    outputs: [{ label: 'Result', dataType: 'result' }],
    configFields: [
      { key: 'toolId', label: 'Tool', type: 'select', options: [], placeholder: 'Select a tool...' },
    ],
  },
  skill: {
    inputs: [{ label: 'Input', dataType: 'text', required: true }],
    outputs: [{ label: 'Result', dataType: 'result' }],
    configFields: [
      { key: 'skillId', label: 'Skill', type: 'select', options: [], placeholder: 'Select a skill...' },
    ],
  },
}

export interface NodeConfig {
  agentId?: string
  skillId?: string
  toolId?: string
  condition?: string
  maxRetries?: number
  timeout?: number
  instruction?: string
  paperIds?: string[]
  [key: string]: any
}

export interface WorkflowNode {
  id: string
  type: WorkflowNodeType
  label: string
  position: { x: number; y: number }
  config: NodeConfig
  status: NodeStatus
  inputs: Port[]
  outputs: Port[]
  result?: any
  error?: string
  startedAt?: Date
  completedAt?: Date
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  sourcePort?: string
  targetPort?: string
  label?: string
  animated: boolean
  active: boolean
}

export interface WorkflowVariable {
  id: string
  name: string
  type: string
  value: any
  description?: string
}

export interface Workflow {
  id: string
  name: string
  description: string
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  variables: WorkflowVariable[]
  createdAt: Date
  updatedAt: Date
}

export interface WorkflowTemplate {
  id: string
  name: string
  description: string
  category: string
  nodes: Omit<WorkflowNode, 'id' | 'status'>[]
  edges: Omit<WorkflowEdge, 'id' | 'active'>[]
}

export interface ExecutionState {
  isRunning: boolean
  isPaused: boolean
  currentNodeId: string | null
  startTime: Date | null
  endTime: Date | null
  progress: number
  logs: ExecutionLog[]
}

export interface ExecutionLog {
  timestamp: Date
  nodeId: string
  level: 'info' | 'warn' | 'error'
  message: string
  data?: any
}

export interface NodeTypeInfo {
  type: WorkflowNodeType
  label: string
  icon: string
  color: string
  description: string
  inputs: number
  outputs: number
  configurable: boolean
}

export const NODE_TYPES: NodeTypeInfo[] = [
  {
    type: 'input',
    label: 'Input',
    icon: '📝',
    color: '#3B82F6',
    description: 'User input node',
    inputs: 0,
    outputs: 1,
    configurable: true,
  },
  {
    type: 'analyze',
    label: 'Analyze',
    icon: '🔍',
    color: '#8B5CF6',
    description: 'Task analysis node',
    inputs: 1,
    outputs: 2,
    configurable: false,
  },
  {
    type: 'decompose',
    label: 'Decompose',
    icon: '✂️',
    color: '#F59E0B',
    description: 'Task decomposition node',
    inputs: 1,
    outputs: 1,
    configurable: false,
  },
  {
    type: 'agent',
    label: 'Agent',
    icon: '🤖',
    color: '#10B981',
    description: 'Agent execution node',
    inputs: 1,
    outputs: 1,
    configurable: true,
  },
  {
    type: 'condition',
    label: 'Condition',
    icon: '◇',
    color: '#6366F1',
    description: 'Conditional branch node',
    inputs: 1,
    outputs: 2,
    configurable: true,
  },
  {
    type: 'parallel',
    label: 'Parallel',
    icon: '⋮',
    color: '#EC4899',
    description: 'Parallel execution node',
    inputs: 1,
    outputs: 3,
    configurable: true,
  },
  {
    type: 'synthesize',
    label: 'Synthesize',
    icon: '🔄',
    color: '#14B8A6',
    description: 'Result synthesis node',
    inputs: 3,
    outputs: 1,
    configurable: false,
  },
  {
    type: 'output',
    label: 'Output',
    icon: '📤',
    color: '#EF4444',
    description: 'Final output node',
    inputs: 1,
    outputs: 0,
    configurable: false,
  },
  {
    type: 'tool',
    label: 'Tool',
    icon: '🔧',
    color: '#64748B',
    description: 'Tool call node',
    inputs: 1,
    outputs: 1,
    configurable: true,
  },
  {
    type: 'skill',
    label: 'Skill',
    icon: '⚡',
    color: '#F97316',
    description: 'Skill call node',
    inputs: 1,
    outputs: 1,
    configurable: true,
  },
]

export function getNodeTypeInfo(type: WorkflowNodeType): NodeTypeInfo {
  return NODE_TYPES.find(n => n.type === type) || NODE_TYPES[0]
}

export function createNode(
  type: WorkflowNodeType,
  position: { x: number; y: number },
  config?: Partial<NodeConfig>
): WorkflowNode {
  const typeInfo = getNodeTypeInfo(type)
  const portDefs = NODE_PORT_DEFINITIONS[type]
  const id = `node_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  
  const inputs: Port[] = portDefs.inputs.map((def, i) => ({
    id: `${id}_in_${i}`,
    type: 'input' as const,
    label: def.label,
    dataType: def.dataType,
    required: def.required ?? false,
    connected: false,
  }))
  
  const outputs: Port[] = portDefs.outputs.map((def, i) => ({
    id: `${id}_out_${i}`,
    type: 'output' as const,
    label: def.label,
    dataType: def.dataType,
    required: false,
    connected: false,
  }))
  
  return {
    id,
    type,
    label: typeInfo.label,
    position,
    config: config || {},
    status: 'idle',
    inputs,
    outputs,
  }
}

export function createEdge(
  source: string,
  target: string,
  sourcePort?: string,
  targetPort?: string
): WorkflowEdge {
  return {
    id: `edge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    source,
    target,
    sourcePort,
    targetPort,
    animated: false,
    active: false,
  }
}

export const WORKFLOW_TEMPLATES: WorkflowTemplate[] = [
  {
    id: 'quick-summary',
    name: 'Quick Summary',
    description: 'Minimal workflow for quick paper summarization',
    category: 'basic',
    nodes: [
      { 
        type: 'input', 
        label: 'Input', 
        position: { x: 50, y: 150 }, 
        config: { 
          instruction: 'Provide a brief summary of this paper in 3-5 sentences',
          paperIds: []
        }, 
        inputs: [], 
        outputs: [{ id: 'out_0', type: 'output', label: 'Output', dataType: 'text', required: false, connected: false }]
      },
      { 
        type: 'skill', 
        label: 'Summary Skill', 
        position: { x: 300, y: 150 }, 
        config: { skillId: 'summary' }, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'text', required: true, connected: true }],
        outputs: [{ id: 'out_0', type: 'output', label: 'Result', dataType: 'result', required: false, connected: false }]
      },
      { 
        type: 'output', 
        label: 'Output', 
        position: { x: 550, y: 150 }, 
        config: {}, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'data', required: true, connected: true }],
        outputs: []
      },
    ],
    edges: [
      { source: 'Input', target: 'Summary Skill', animated: false },
      { source: 'Summary Skill', target: 'Output', animated: false },
    ],
  },
  {
    id: 'paper-analysis',
    name: 'Paper Analysis',
    description: 'Simple paper analysis workflow - analyzes a paper and provides summary',
    category: 'basic',
    nodes: [
      { 
        type: 'input', 
        label: 'Input', 
        position: { x: 50, y: 150 }, 
        config: { 
          instruction: 'Analyze and summarize the key contributions, methodology, and findings of this paper',
          paperIds: []
        }, 
        inputs: [], 
        outputs: [{ id: 'out_0', type: 'output', label: 'Output', dataType: 'text', required: false, connected: false }]
      },
      { 
        type: 'agent', 
        label: 'Research Agent', 
        position: { x: 300, y: 150 }, 
        config: { 
          agentId: 'research-agent',
          timeout: 300,
          maxRetries: 1
        }, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'text', required: true, connected: true }],
        outputs: [{ id: 'out_0', type: 'output', label: 'Result', dataType: 'result', required: false, connected: false }]
      },
      { 
        type: 'output', 
        label: 'Output', 
        position: { x: 550, y: 150 }, 
        config: {}, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'data', required: true, connected: true }],
        outputs: []
      },
    ],
    edges: [
      { source: 'Input', target: 'Research Agent', animated: false },
      { source: 'Research Agent', target: 'Output', animated: false },
    ],
  },
  {
    id: 'multi-agent',
    name: 'Multi-Agent Collaboration',
    description: 'Complex workflow with task decomposition, parallel execution, and result synthesis',
    category: 'advanced',
    nodes: [
      { 
        type: 'input', 
        label: 'Input', 
        position: { x: 50, y: 200 }, 
        config: { 
          instruction: 'Conduct a comprehensive analysis of this paper including methodology review, key findings, and future research directions',
          paperIds: []
        }, 
        inputs: [], 
        outputs: [{ id: 'out_0', type: 'output', label: 'Output', dataType: 'text', required: false, connected: false }]
      },
      { 
        type: 'analyze', 
        label: 'Analyze Task', 
        position: { x: 280, y: 200 }, 
        config: {}, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'text', required: true, connected: true }],
        outputs: [
          { id: 'out_0', type: 'output', label: 'Analysis', dataType: 'analysis', required: false, connected: false },
          { id: 'out_1', type: 'output', label: 'Metadata', dataType: 'data', required: false, connected: false }
        ]
      },
      { 
        type: 'decompose', 
        label: 'Decompose', 
        position: { x: 510, y: 200 }, 
        config: {}, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'text', required: true, connected: true }],
        outputs: [{ id: 'out_0', type: 'output', label: 'Tasks', dataType: 'task', required: false, connected: false }]
      },
      { 
        type: 'agent', 
        label: 'Research', 
        position: { x: 740, y: 50 }, 
        config: { 
          agentId: 'research-agent',
          instruction: 'Research and extract key information from the paper'
        }, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'text', required: true, connected: true }],
        outputs: [{ id: 'out_0', type: 'output', label: 'Result', dataType: 'result', required: false, connected: false }]
      },
      { 
        type: 'agent', 
        label: 'Analysis', 
        position: { x: 740, y: 200 }, 
        config: { 
          agentId: 'analysis-agent',
          instruction: 'Analyze the methodology and experimental design'
        }, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'text', required: true, connected: true }],
        outputs: [{ id: 'out_0', type: 'output', label: 'Result', dataType: 'result', required: false, connected: false }]
      },
      { 
        type: 'agent', 
        label: 'Writer', 
        position: { x: 740, y: 350 }, 
        config: { 
          agentId: 'writer-agent',
          instruction: 'Summarize findings and write conclusions'
        }, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'text', required: true, connected: true }],
        outputs: [{ id: 'out_0', type: 'output', label: 'Result', dataType: 'result', required: false, connected: false }]
      },
      { 
        type: 'synthesize', 
        label: 'Synthesize', 
        position: { x: 970, y: 200 }, 
        config: {}, 
        inputs: [
          { id: 'in_0', type: 'input', label: 'Input 1', dataType: 'data', required: true, connected: true },
          { id: 'in_1', type: 'input', label: 'Input 2', dataType: 'data', required: true, connected: true },
          { id: 'in_2', type: 'input', label: 'Input 3', dataType: 'data', required: true, connected: true }
        ],
        outputs: [{ id: 'out_0', type: 'output', label: 'Result', dataType: 'result', required: false, connected: false }]
      },
      { 
        type: 'output', 
        label: 'Output', 
        position: { x: 1200, y: 200 }, 
        config: {}, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'data', required: true, connected: true }],
        outputs: []
      },
    ],
    edges: [
      { source: 'Input', target: 'Analyze Task', animated: false },
      { source: 'Analyze Task', target: 'Decompose', animated: false },
      { source: 'Decompose', target: 'Research', animated: false },
      { source: 'Decompose', target: 'Analysis', animated: false },
      { source: 'Decompose', target: 'Writer', animated: false },
      { source: 'Research', target: 'Synthesize', animated: false },
      { source: 'Analysis', target: 'Synthesize', animated: false },
      { source: 'Writer', target: 'Synthesize', animated: false },
      { source: 'Synthesize', target: 'Output', animated: false },
    ],
  },
  {
    id: 'conditional-flow',
    name: 'Conditional Flow',
    description: 'Workflow with conditional branching based on task complexity',
    category: 'advanced',
    nodes: [
      { 
        type: 'input', 
        label: 'Input', 
        position: { x: 100, y: 200 }, 
        config: {}, 
        inputs: [], 
        outputs: [{ id: 'out_0', type: 'output', label: 'Output', dataType: 'text', required: false, connected: false }]
      },
      { 
        type: 'analyze', 
        label: 'Analyze', 
        position: { x: 250, y: 200 }, 
        config: {}, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'text', required: true, connected: true }],
        outputs: [
          { id: 'out_0', type: 'output', label: 'Analysis', dataType: 'analysis', required: false, connected: false },
          { id: 'out_1', type: 'output', label: 'Metadata', dataType: 'data', required: false, connected: false }
        ]
      },
      { 
        type: 'condition', 
        label: 'Complexity?', 
        position: { x: 400, y: 200 }, 
        config: { condition: "complexity == 'high'" }, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'text', required: true, connected: true }],
        outputs: [
          { id: 'out_0', type: 'output', label: 'True', dataType: 'any', required: false, connected: false },
          { id: 'out_1', type: 'output', label: 'False', dataType: 'any', required: false, connected: false }
        ]
      },
      { 
        type: 'agent', 
        label: 'Simple Agent', 
        position: { x: 550, y: 100 }, 
        config: {}, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'text', required: true, connected: true }],
        outputs: [{ id: 'out_0', type: 'output', label: 'Result', dataType: 'result', required: false, connected: false }]
      },
      { 
        type: 'parallel', 
        label: 'Team', 
        position: { x: 550, y: 300 }, 
        config: {}, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'text', required: true, connected: true }],
        outputs: [{ id: 'out_0', type: 'output', label: 'Output', dataType: 'any', required: false, connected: false }]
      },
      { 
        type: 'output', 
        label: 'Output', 
        position: { x: 700, y: 200 }, 
        config: {}, 
        inputs: [{ id: 'in_0', type: 'input', label: 'Input', dataType: 'data', required: true, connected: true }],
        outputs: []
      },
    ],
    edges: [
      { source: 'Input', target: 'Analyze', animated: false },
      { source: 'Analyze', target: 'Complexity?', animated: false },
      { source: 'Complexity?', target: 'Simple Agent', animated: false },
      { source: 'Complexity?', target: 'Team', animated: false },
      { source: 'Simple Agent', target: 'Output', animated: false },
      { source: 'Team', target: 'Output', animated: false },
    ],
  },
]
