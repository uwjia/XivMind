import CustomNode from '@/components/team/CustomNode.vue'
import type { WorkflowNode } from '@/types/workflow'

export default {
  title: 'Components/Team/CustomNode',
  component: CustomNode,
  tags: ['autodocs'],
  argTypes: {
    isSelected: {
      control: 'boolean',
      description: 'Whether the node is selected'
    },
    agents: {
      control: 'object',
      description: 'List of available agents'
    },
    skills: {
      control: 'object',
      description: 'List of available skills'
    }
  }
}

const createNode = (type: string, label: string, status: string = 'idle'): WorkflowNode => ({
  id: `node-${type}`,
  type: type as any,
  label,
  position: { x: 0, y: 0 },
  status: status as any,
  inputs: [
    { id: 'in-1', type: 'input' as const, label: 'Input', dataType: 'text' as const, required: false, connected: false }
  ],
  outputs: [
    { id: 'out-1', type: 'output' as const, label: 'Output', dataType: 'text' as const, required: false, connected: false }
  ],
  config: {}
})

export const InputNode = {
  args: {
    node: createNode('input', 'Task Input'),
    isSelected: false
  }
}

export const AgentNode = {
  args: {
    node: createNode('agent', 'Research Agent'),
    isSelected: false,
    agents: ['Agent-1', 'Agent-2', 'Agent-3']
  }
}

export const ConditionNode = {
  args: {
    node: {
      ...createNode('condition', 'Check Complexity'),
      config: { condition: 'complexity == "high"' }
    },
    isSelected: false
  }
}

export const ParallelNode = {
  args: {
    node: createNode('parallel', 'Parallel Execution'),
    isSelected: false
  }
}

export const OutputNode = {
  args: {
    node: createNode('output', 'Final Result'),
    isSelected: false
  }
}

export const SelectedNode = {
  args: {
    node: createNode('agent', 'Selected Agent'),
    isSelected: true
  }
}

export const RunningNode = {
  args: {
    node: createNode('agent', 'Processing...', 'running'),
    isSelected: false
  }
}

export const SuccessNode = {
  args: {
    node: createNode('agent', 'Completed', 'success'),
    isSelected: false
  }
}

export const ErrorNode = {
  args: {
    node: createNode('agent', 'Failed', 'error'),
    isSelected: false
  }
}

export const AllNodeTypes = {
  render: () => ({
    components: { CustomNode },
    setup() {
      const nodes = [
        { node: createNode('input', 'Input'), type: 'input' },
        { node: createNode('agent', 'Agent'), type: 'agent' },
        { node: createNode('condition', 'Condition'), type: 'condition' },
        { node: createNode('parallel', 'Parallel'), type: 'parallel' },
        { node: createNode('synthesize', 'Synthesize'), type: 'synthesize' },
        { node: createNode('output', 'Output'), type: 'output' }
      ]
      return { nodes }
    },
    template: `
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; padding: 24px; background: var(--bg-secondary);">
        <div v-for="item in nodes" :key="item.type" style="position: relative; height: 120px;">
          <CustomNode :node="item.node" :is-selected="false" />
        </div>
      </div>
    `
  })
}

export const AllStatuses = {
  render: () => ({
    components: { CustomNode },
    setup() {
      const nodes = [
        { node: createNode('agent', 'Idle', 'idle'), status: 'idle' },
        { node: createNode('agent', 'Running', 'running'), status: 'running' },
        { node: createNode('agent', 'Success', 'success'), status: 'success' },
        { node: createNode('agent', 'Error', 'error'), status: 'error' }
      ]
      return { nodes }
    },
    template: `
      <div style="display: flex; gap: 24px; padding: 24px; background: var(--bg-secondary);">
        <div v-for="item in nodes" :key="item.status" style="position: relative; height: 120px;">
          <CustomNode :node="item.node" :is-selected="false" />
        </div>
      </div>
    `
  })
}
