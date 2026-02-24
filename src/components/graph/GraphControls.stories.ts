import GraphControls from './GraphControls.vue'
import type { Meta, StoryObj } from '@storybook/vue3'

const meta: Meta<typeof GraphControls> = {
  title: 'Components/Graph/GraphControls',
  component: GraphControls,
  tags: ['autodocs'],
  argTypes: {
    config: {
      control: 'object',
      description: 'Graph configuration object'
    },
    categories: {
      control: 'object',
      description: 'List of categories with counts and colors'
    }
  }
}

export default meta
type Story = StoryObj<typeof GraphControls>

const defaultConfig = {
  similarityThreshold: 0.6,
  nodeSizeFactor: 1,
  showLabels: true,
  layoutType: 'force' as const,
  selectedCategories: []
}

const defaultCategories = [
  { name: 'cs.AI', count: 45, color: '#FF6B6B' },
  { name: 'cs.CV', count: 38, color: '#45B7D1' },
  { name: 'cs.LG', count: 32, color: '#96CEB4' },
  { name: 'cs.CL', count: 28, color: '#4ECDC4' },
  { name: 'cs.NE', count: 15, color: '#FFEAA7' }
]

export const Default: Story = {
  args: {
    config: defaultConfig,
    categories: defaultCategories
  }
}

export const WithSelectedCategories: Story = {
  args: {
    config: {
      ...defaultConfig,
      selectedCategories: ['cs.AI', 'cs.CV']
    },
    categories: defaultCategories
  }
}

export const HighThreshold: Story = {
  args: {
    config: {
      ...defaultConfig,
      similarityThreshold: 0.8
    },
    categories: defaultCategories
  }
}

export const HiddenLabels: Story = {
  args: {
    config: {
      ...defaultConfig,
      showLabels: false
    },
    categories: defaultCategories
  }
}
