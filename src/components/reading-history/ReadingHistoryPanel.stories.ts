import type { Meta, StoryObj } from '@storybook/vue3'
import ReadingHistoryPanel from '@/components/reading-history/ReadingHistoryPanel.vue'

const meta: Meta<typeof ReadingHistoryPanel> = {
  title: 'Components/ReadingHistory/ReadingHistoryPanel',
  component: ReadingHistoryPanel,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen'
  },
  decorators: [
    () => ({
      template: `
        <div style="width: 100vw; height: 100vh; background: #1a1a2e;">
          <story />
        </div>
      `
    })
  ]
}

export default meta
type Story = StoryObj<typeof ReadingHistoryPanel>

export const Default: Story = {
  render: () => ({
    components: { ReadingHistoryPanel },
    template: '<ReadingHistoryPanel />'
  })
}

export const Hidden: Story = {
  render: () => ({
    components: { ReadingHistoryPanel },
    setup() {
      return {}
    },
    template: '<ReadingHistoryPanel />'
  })
}

export const Minimized: Story = {
  render: () => ({
    components: { ReadingHistoryPanel },
    setup() {
      return {}
    },
    template: '<ReadingHistoryPanel />'
  })
}

export const Loading: Story = {
  render: () => ({
    components: { ReadingHistoryPanel },
    setup() {
      return {}
    },
    template: '<ReadingHistoryPanel />'
  })
}

export const Error: Story = {
  render: () => ({
    components: { ReadingHistoryPanel },
    setup() {
      return {}
    },
    template: '<ReadingHistoryPanel />'
  })
}

export const Empty: Story = {
  render: () => ({
    components: { ReadingHistoryPanel },
    setup() {
      return {}
    },
    template: '<ReadingHistoryPanel />'
  })
}

export const SingleItem: Story = {
  render: () => ({
    components: { ReadingHistoryPanel },
    setup() {
      return {}
    },
    template: '<ReadingHistoryPanel />'
  })
}

export const ManyItems: Story = {
  render: () => ({
    components: { ReadingHistoryPanel },
    setup() {
      return {}
    },
    template: '<ReadingHistoryPanel />'
  })
}

export const AllCompleted: Story = {
  render: () => ({
    components: { ReadingHistoryPanel },
    setup() {
      return {}
    },
    template: '<ReadingHistoryPanel />'
  })
}

export const JustStarted: Story = {
  render: () => ({
    components: { ReadingHistoryPanel },
    setup() {
      return {}
    },
    template: '<ReadingHistoryPanel />'
  })
}
