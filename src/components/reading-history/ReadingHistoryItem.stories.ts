import type { Meta, StoryObj } from '@storybook/vue3'
import ReadingHistoryItem from '@/components/reading-history/ReadingHistoryItem.vue'
import type { ReadingHistoryItem as ReadingHistoryItemType } from '@/services/readingHistory'

const meta: Meta<typeof ReadingHistoryItem> = {
  title: 'Components/ReadingHistory/ReadingHistoryItem',
  component: ReadingHistoryItem,
  tags: ['autodocs'],
  argTypes: {
    item: {
      control: 'object',
      description: 'Reading history item to display'
    }
  }
}

export default meta
type Story = StoryObj<typeof ReadingHistoryItem>

const createHistoryItem = (overrides: Partial<ReadingHistoryItemType> = {}): ReadingHistoryItemType => ({
  paper_id: '2301.12345',
  title: 'Attention Is All You Need: Transformer Architecture for Sequence Modeling',
  authors: ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar'],
  primary_category: 'cs.CL',
  categories: ['cs.CL', 'cs.LG'],
  current_page: 5,
  total_pages: 15,
  progress_percent: 33.3,
  last_read_at: new Date().toISOString(),
  pdf_url: 'https://arxiv.org/pdf/2301.12345',
  abs_url: 'https://arxiv.org/abs/2301.12345',
  published: '2023-01-15',
  ...overrides
})

export const Default: Story = {
  args: {
    item: createHistoryItem()
  }
}

export const JustRead: Story = {
  args: {
    item: createHistoryItem({
      last_read_at: new Date().toISOString()
    })
  }
}

export const ReadHourAgo: Story = {
  args: {
    item: createHistoryItem({
      last_read_at: new Date(Date.now() - 3600000).toISOString()
    })
  }
}

export const ReadDayAgo: Story = {
  args: {
    item: createHistoryItem({
      last_read_at: new Date(Date.now() - 86400000).toISOString()
    })
  }
}

export const ReadWeekAgo: Story = {
  args: {
    item: createHistoryItem({
      last_read_at: new Date(Date.now() - 7 * 86400000).toISOString()
    })
  }
}

export const Completed: Story = {
  args: {
    item: createHistoryItem({
      current_page: 15,
      total_pages: 15,
      progress_percent: 100
    })
  }
}

export const JustStarted: Story = {
  args: {
    item: createHistoryItem({
      current_page: 1,
      total_pages: 20,
      progress_percent: 5
    })
  }
}

export const HalfwayThrough: Story = {
  args: {
    item: createHistoryItem({
      current_page: 10,
      total_pages: 20,
      progress_percent: 50
    })
  }
}

export const LongTitle: Story = {
  args: {
    item: createHistoryItem({
      title: 'A Very Long Paper Title That Demonstrates How The Component Handles Excessively Long Titles And Whether It Properly Truncates Them With Ellipsis When Displayed In The UI'
    })
  }
}

export const DifferentCategory: Story = {
  args: {
    item: createHistoryItem({
      title: 'Deep Reinforcement Learning for Game Playing',
      primary_category: 'cs.AI',
      categories: ['cs.AI', 'cs.LG']
    })
  }
}

export const ComputerVision: Story = {
  args: {
    item: createHistoryItem({
      title: 'Vision Transformer: An Image is Worth 16x16 Words',
      primary_category: 'cs.CV',
      categories: ['cs.CV', 'cs.LG']
    })
  }
}

export const ManyAuthors: Story = {
  args: {
    item: createHistoryItem({
      title: 'Large-Scale Distributed Training',
      authors: ['Author One', 'Author Two', 'Author Three', 'Author Four', 'Author Five', 'Author Six']
    })
  }
}
