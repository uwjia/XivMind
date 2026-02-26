import SubAgentCard from './SubAgentCard.vue'
import type { SubAgent } from '../../types/subagent'

export default {
  title: 'Components/SubAgents/SubAgentCard',
  component: SubAgentCard,
  tags: ['autodocs'],
  argTypes: {
    agent: {
      control: 'object',
      description: 'SubAgent data object'
    },
    selected: {
      control: 'boolean',
      description: 'Whether the agent is selected'
    },
    showActions: {
      control: 'boolean',
      description: 'Whether to show action buttons'
    }
  }
}

const defaultAgent: SubAgent = {
  id: 'research-agent',
  name: 'Research Assistant',
  description: 'Specialized in literature search and research analysis, helping users discover and organize academic resources',
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

const dynamicAgent: SubAgent = {
  id: 'analysis-agent',
  name: 'Analysis Assistant',
  description: 'Specialized in deep analysis and comparative research, discovering research trends and key insights',
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

const chineseAgent: SubAgent = {
  id: 'writer-agent',
  name: '写作助手',
  description: '专注于学术写作，包括文献综述、摘要生成和论文评述',
  icon: 'pen',
  skills: ['summary', 'translation'],
  tools: ['get_paper_details', 'execute_skill'],
  max_turns: 10,
  temperature: 0.5,
  model: 'gpt-4o-mini',
  provider: 'openai',
  available: true,
  source: 'dynamic',
  language: 'zh'
}

const unavailableAgent: SubAgent = {
  id: 'disabled-agent',
  name: 'Disabled Agent',
  description: 'This agent is not available due to missing API configuration',
  icon: 'bot',
  skills: [],
  tools: [],
  max_turns: 10,
  temperature: 0.7,
  available: false,
  source: 'builtin',
  language: 'en'
}

export const Default = {
  args: {
    agent: defaultAgent
  }
}

export const Dynamic = {
  args: {
    agent: dynamicAgent
  }
}

export const Chinese = {
  args: {
    agent: chineseAgent
  }
}

export const Unavailable = {
  args: {
    agent: unavailableAgent
  }
}

export const Selected = {
  args: {
    agent: defaultAgent,
    selected: true
  }
}

export const WithActions = {
  args: {
    agent: dynamicAgent,
    showActions: true
  }
}

export const AllVariants = {
  render: () => ({
    components: { SubAgentCard },
    setup() {
      const agents: SubAgent[] = [
        defaultAgent,
        dynamicAgent,
        chineseAgent,
        unavailableAgent
      ]
      return { agents }
    },
    template: `
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; max-width: 900px;">
        <SubAgentCard 
          v-for="agent in agents" 
          :key="agent.id" 
          :agent="agent"
          :show-actions="agent.source === 'dynamic'"
        />
      </div>
    `
  })
}
