import GraphLegend from './GraphLegend.vue'
import type { Meta, StoryObj } from '@storybook/vue3'

const meta: Meta<typeof GraphLegend> = {
  title: 'Components/Graph/GraphLegend',
  component: GraphLegend,
  tags: ['autodocs'],
  argTypes: {
    categories: {
      control: 'object',
      description: 'List of categories with counts and colors'
    }
  }
}

export default meta
type Story = StoryObj<typeof GraphLegend>

const defaultCategories = [
  { name: 'cs.AI', count: 45, color: '#FF6B6B' },
  { name: 'cs.CV', count: 38, color: '#45B7D1' },
  { name: 'cs.LG', count: 32, color: '#96CEB4' },
  { name: 'cs.CL', count: 28, color: '#4ECDC4' },
  { name: 'cs.NE', count: 15, color: '#FFEAA7' }
]

const manyCategories = [
  { name: 'cs.AI', count: 45, color: '#FF6B6B' },
  { name: 'cs.CV', count: 38, color: '#45B7D1' },
  { name: 'cs.LG', count: 32, color: '#96CEB4' },
  { name: 'cs.CL', count: 28, color: '#4ECDC4' },
  { name: 'cs.NE', count: 15, color: '#FFEAA7' },
  { name: 'cs.RO', count: 12, color: '#DDA0DD' },
  { name: 'cs.CR', count: 10, color: '#98D8C8' },
  { name: 'cs.DB', count: 8, color: '#F7DC6F' }
]

export const Default: Story = {
  args: {
    categories: defaultCategories
  }
}

export const ManyCategories: Story = {
  args: {
    categories: manyCategories
  },
  parameters: {
    docs: {
      description: {
        story: 'Shows legend with more than 5 categories (only first 5 are displayed with "more" indicator).'
      }
    }
  }
}

export const SingleCategory: Story = {
  args: {
    categories: [{ name: 'cs.AI', count: 100, color: '#FF6B6B' }]
  }
}
