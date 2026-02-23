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
    }
  },
  parameters: {
    layout: 'fullscreen'
  }
}

export default meta
type Story = StoryObj<typeof MonthView>

export const Default: Story = {
  args: {
    year: 2024,
    month: 0
  }
}

export const February: Story = {
  args: {
    year: 2024,
    month: 1
  }
}

export const EmptyMonth: Story = {
  args: {
    year: 2024,
    month: 11
  }
}

export const CurrentMonth: Story = {
  args: {
    year: new Date().getFullYear(),
    month: new Date().getMonth()
  }
}
