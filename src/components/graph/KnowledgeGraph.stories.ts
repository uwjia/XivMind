import KnowledgeGraph from './KnowledgeGraph.vue'
import type { Meta, StoryObj } from '@storybook/vue3'

const meta: Meta<typeof KnowledgeGraph> = {
  title: 'Components/Graph/KnowledgeGraph',
  component: KnowledgeGraph,
  tags: ['autodocs'],
  argTypes: {
    date: {
      control: 'text',
      description: 'Date string for the graph'
    }
  }
}

export default meta
type Story = StoryObj<typeof KnowledgeGraph>

export const Default: Story = {
  args: {
    date: '2024-02-19'
  }
}

export const WithLoading: Story = {
  args: {
    date: '2024-02-19'
  },
  parameters: {
    docs: {
      description: {
        story: 'Shows the loading state while graph data is being fetched.'
      }
    }
  }
}
