import MonthView from './MonthView.vue'
import type { Meta, StoryObj } from '@storybook/vue3'

const meta: Meta<typeof MonthView> = {
  title: 'Components/MonthView',
  component: MonthView,
  tags: ['autodocs'],
  argTypes: {
    year: {
      control: 'number',
      description: 'Year to display'
    },
    month: {
      control: 'select',
      description: 'Month to display (0-11)',
      options: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
      mapping: {
        0: 'January',
        1: 'February',
        2: 'March',
        3: 'April',
        4: 'May',
        5: 'June',
        6: 'July',
        7: 'August',
        8: 'September',
        9: 'October',
        10: 'November',
        11: 'December'
      }
    },
    indexes: {
      control: 'object',
      description: 'Array of date indexes with stored paper counts'
    },
    fetchingDates: {
      control: 'object',
      description: 'Set of dates currently being fetched'
    }
  },
  parameters: {
    layout: 'fullscreen'
  }
}

export default meta
type Story = StoryObj<typeof MonthView>

const mockIndexes = [
  { date: '2024-01-01', total_count: 150, fetched_at: '2024-01-01T10:00:00' },
  { date: '2024-01-02', total_count: 120, fetched_at: '2024-01-02T10:00:00' },
  { date: '2024-01-03', total_count: 0, fetched_at: '2024-01-03T10:00:00' },
  { date: '2024-01-05', total_count: 200, fetched_at: '2024-01-05T10:00:00' },
  { date: '2024-01-08', total_count: 180, fetched_at: '2024-01-08T10:00:00' },
  { date: '2024-01-10', total_count: 95, fetched_at: '2024-01-10T10:00:00' },
  { date: '2024-01-15', total_count: 210, fetched_at: '2024-01-15T10:00:00' },
  { date: '2024-01-20', total_count: 175, fetched_at: '2024-01-20T10:00:00' },
  { date: '2024-01-25', total_count: 160, fetched_at: '2024-01-25T10:00:00' }
]

export const Default: Story = {
  args: {
    year: 2024,
    month: 0,
    indexes: mockIndexes,
    fetchingDates: new Set<string>()
  }
}

export const February: Story = {
  args: {
    year: 2024,
    month: 1,
    indexes: [
      { date: '2024-02-01', total_count: 130, fetched_at: '2024-02-01T10:00:00' },
      { date: '2024-02-14', total_count: 200, fetched_at: '2024-02-14T10:00:00' },
      { date: '2024-02-28', total_count: 145, fetched_at: '2024-02-28T10:00:00' }
    ],
    fetchingDates: new Set<string>()
  }
}

export const WithFetching: Story = {
  args: {
    year: 2024,
    month: 0,
    indexes: mockIndexes,
    fetchingDates: new Set(['2024-01-04', '2024-01-06'])
  }
}

export const EmptyMonth: Story = {
  args: {
    year: 2024,
    month: 11,
    indexes: [],
    fetchingDates: new Set<string>()
  }
}

export const CurrentMonth: Story = {
  args: {
    year: new Date().getFullYear(),
    month: new Date().getMonth(),
    indexes: [
      { date: new Date().toISOString().split('T')[0], total_count: 100, fetched_at: new Date().toISOString() }
    ],
    fetchingDates: new Set<string>()
  }
}

export const FullyStored: Story = {
  args: {
    year: 2024,
    month: 0,
    indexes: Array.from({ length: 31 }, (_, i) => ({
      date: `2024-01-${String(i + 1).padStart(2, '0')}`,
      total_count: Math.floor(Math.random() * 200) + 50,
      fetched_at: `2024-01-${String(i + 1).padStart(2, '0')}T10:00:00`
    })),
    fetchingDates: new Set<string>()
  }
}
