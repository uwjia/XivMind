import GraphStatistics from './GraphStatistics.vue'
import type { Meta, StoryObj } from '@storybook/vue3'
import type { GraphStatistics as GraphStatisticsType } from '../../types/graph'

const meta: Meta<typeof GraphStatistics> = {
  title: 'Components/Graph/GraphStatistics',
  component: GraphStatistics,
  tags: ['autodocs'],
  argTypes: {
    statistics: {
      control: 'object',
      description: 'Graph statistics data'
    }
  }
}

export default meta
type Story = StoryObj<typeof GraphStatistics>

const defaultStatistics: GraphStatisticsType = {
  totalPapers: 156,
  totalConnections: 234,
  topCategories: [
    { categoryId: 'cs.AI', categoryName: 'cs.AI', count: 45 },
    { categoryId: 'cs.CV', categoryName: 'cs.CV', count: 38 },
    { categoryId: 'cs.LG', categoryName: 'cs.LG', count: 32 }
  ],
  avgSimilarity: 0.72,
  clusters: []
}

const smallGraphStatistics: GraphStatisticsType = {
  totalPapers: 25,
  totalConnections: 42,
  topCategories: [
    { categoryId: 'cs.AI', categoryName: 'cs.AI', count: 15 },
    { categoryId: 'cs.LG', categoryName: 'cs.LG', count: 10 }
  ],
  avgSimilarity: 0.85,
  clusters: []
}

const largeGraphStatistics: GraphStatisticsType = {
  totalPapers: 892,
  totalConnections: 1567,
  topCategories: [
    { categoryId: 'cs.AI', categoryName: 'cs.AI', count: 245 },
    { categoryId: 'cs.CV', categoryName: 'cs.CV', count: 198 },
    { categoryId: 'cs.LG', categoryName: 'cs.LG', count: 176 },
    { categoryId: 'cs.CL', categoryName: 'cs.CL', count: 142 },
    { categoryId: 'cs.NE', categoryName: 'cs.NE', count: 131 }
  ],
  avgSimilarity: 0.58,
  clusters: []
}

export const Default: Story = {
  args: {
    statistics: defaultStatistics
  }
}

export const SmallGraph: Story = {
  args: {
    statistics: smallGraphStatistics
  },
  parameters: {
    docs: {
      description: {
        story: 'Statistics for a small graph with few papers.'
      }
    }
  }
}

export const LargeGraph: Story = {
  args: {
    statistics: largeGraphStatistics
  },
  parameters: {
    docs: {
      description: {
        story: 'Statistics for a large graph with many papers and connections.'
      }
    }
  }
}

export const Empty: Story = {
  args: {
    statistics: null
  },
  parameters: {
    docs: {
      description: {
        story: 'Shows the component when no statistics are available.'
      }
    }
  }
}
