import SubAgentForm from './SubAgentForm.vue'
import type { SubAgent } from '../../types/subagent'

export default {
  title: 'Components/SubAgents/SubAgentForm',
  component: SubAgentForm,
  tags: ['autodocs'],
  argTypes: {
    agent: {
      control: 'object',
      description: 'SubAgent data object'
    },
    executing: {
      control: 'boolean',
      description: 'Whether the agent is currently executing'
    }
  }
}

const defaultAgent: SubAgent = {
  id: 'research-agent',
  name: 'Research Assistant',
  description: 'Specialized in literature search and research analysis',
  icon: 'search',
  skills: ['summary', 'related-papers', 'citation'],
  tools: ['search_papers', 'get_paper_details', 'execute_skill'],
  max_turns: 15,
  temperature: 0.3,
  model: 'gpt-4o-mini',
  provider: 'openai',
  available: true,
  source: 'builtin',
  language: 'en'
}

const analysisAgent: SubAgent = {
  id: 'analysis-agent',
  name: 'Analysis Assistant',
  description: 'Specialized in deep analysis and comparative research',
  icon: 'chart-bar',
  skills: ['summary', 'citation'],
  tools: ['get_paper_details', 'execute_skill'],
  max_turns: 12,
  temperature: 0.4,
  model: 'gpt-4o-mini',
  provider: 'openai',
  available: true,
  source: 'dynamic',
  language: 'en'
}

export const Default = {
  args: {
    agent: defaultAgent,
    executing: false
  }
}

export const DynamicAgent = {
  args: {
    agent: analysisAgent,
    executing: false
  }
}

export const Executing = {
  args: {
    agent: defaultAgent,
    executing: true
  }
}

export const WithPaperIds = {
  args: {
    agent: defaultAgent,
    executing: false
  },
  render: () => ({
    components: { SubAgentForm },
    setup() {
      return { agent: defaultAgent }
    },
    template: `
      <div style="max-width: 600px;">
        <SubAgentForm :agent="agent" />
      </div>
    `
  })
}
