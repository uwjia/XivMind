import type { Meta, StoryObj } from '@storybook/vue3'
import MemoryToggle from '@/components/chat/MemoryToggle.vue'

const meta: Meta<typeof MemoryToggle> = {
  title: 'Components/Chat/MemoryToggle',
  component: MemoryToggle,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#1a1a2e' },
        { name: 'light', value: '#f5f5f5' },
      ],
    },
  },
}

export default meta
type Story = StoryObj<typeof MemoryToggle>

export const Default: Story = {
  args: {},
}

export const MemoryEnabled: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const checkbox = canvasElement.querySelector('input[type="checkbox"]') as HTMLInputElement
    if (checkbox && !checkbox.checked) {
      checkbox.click()
    }
  },
}

export const MemoryDisabled: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const checkbox = canvasElement.querySelector('input[type="checkbox"]') as HTMLInputElement
    if (checkbox && checkbox.checked) {
      checkbox.click()
    }
  },
}

export const InToolbar: Story = {
  decorators: [
    () => ({
      template: `
        <div style="display: flex; align-items: center; gap: 16px; padding: 16px; background: #263238; border-radius: 8px;">
          <span style="color: #90a4ae;">Ask Mode</span>
          <story />
          <span style="color: #90a4ae;">|</span>
          <span style="color: #90a4ae;">History</span>
        </div>
      `,
    }),
  ],
  args: {},
}
