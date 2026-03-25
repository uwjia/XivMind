import type { Meta, StoryObj } from '@storybook/vue3'
import CategoryDistribution from './CategoryDistribution.vue'
import type { CategoryDistribution as CategoryDistributionType } from '@/types/author'

const meta: Meta<typeof CategoryDistribution> = {
  title: 'Author/CategoryDistribution',
  component: CategoryDistribution,
  tags: ['autodocs'],
  argTypes: {
    categories: {
      description: 'Array of category distribution data',
      control: 'object',
    },
  },
}

export default meta
type Story = StoryObj<typeof CategoryDistribution>

const sampleCategories: CategoryDistributionType[] = [
  { category: 'cs.AI', name: 'Artificial Intelligence', count: 45, percentage: 35 },
  { category: 'cs.LG', name: 'Machine Learning', count: 38, percentage: 30 },
  { category: 'cs.CL', name: 'Computation and Language', count: 25, percentage: 20 },
  { category: 'cs.CV', name: 'Computer Vision', count: 12, percentage: 10 },
  { category: 'cs.NE', name: 'Neural and Evolutionary Computing', count: 6, percentage: 5 },
]

export const Default: Story = {
  args: {
    categories: sampleCategories,
  },
}

export const SingleCategory: Story = {
  args: {
    categories: [{ category: 'cs.AI', name: 'Artificial Intelligence', count: 100, percentage: 100 }],
  },
}

export const ManyCategories: Story = {
  args: {
    categories: [
      { category: 'cs.AI', name: 'Artificial Intelligence', count: 30, percentage: 20 },
      { category: 'cs.LG', name: 'Machine Learning', count: 25, percentage: 17 },
      { category: 'cs.CL', name: 'Computation and Language', count: 20, percentage: 13 },
      { category: 'cs.CV', name: 'Computer Vision', count: 18, percentage: 12 },
      { category: 'cs.NE', name: 'Neural and Evolutionary Computing', count: 15, percentage: 10 },
      { category: 'cs.RO', name: 'Robotics', count: 12, percentage: 8 },
      { category: 'cs.SE', name: 'Software Engineering', count: 10, percentage: 7 },
      { category: 'cs.DB', name: 'Databases', count: 8, percentage: 5 },
      { category: 'cs.CR', name: 'Cryptography and Security', count: 7, percentage: 5 },
      { category: 'cs.HC', name: 'Human-Computer Interaction', count: 5, percentage: 3 },
    ],
  },
}

export const LowCounts: Story = {
  args: {
    categories: [
      { category: 'cs.AI', name: 'Artificial Intelligence', count: 2, percentage: 40 },
      { category: 'cs.LG', name: 'Machine Learning', count: 2, percentage: 40 },
      { category: 'cs.CL', name: 'Computation and Language', count: 1, percentage: 20 },
    ],
  },
}

export const HighCounts: Story = {
  args: {
    categories: [
      { category: 'cs.AI', name: 'Artificial Intelligence', count: 150, percentage: 35 },
      { category: 'cs.LG', name: 'Machine Learning', count: 120, percentage: 28 },
      { category: 'cs.CL', name: 'Computation and Language', count: 80, percentage: 19 },
      { category: 'cs.CV', name: 'Computer Vision', count: 50, percentage: 12 },
      { category: 'cs.NE', name: 'Neural and Evolutionary Computing', count: 30, percentage: 7 },
    ],
  },
}

export const Empty: Story = {
  args: {
    categories: [],
  },
}
