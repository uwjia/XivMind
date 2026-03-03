import type { Meta, StoryObj } from '@storybook/vue3'
import ChatControls from '@/components/chat/ChatControls.vue'

const meta: Meta<typeof ChatControls> = {
  title: 'Components/Chat/ChatControls',
  component: ChatControls,
  tags: ['autodocs'],
  argTypes: {
    mode: {
      control: 'select',
      options: ['search', 'ask'],
      description: 'Current chat mode'
    },
    showHistoryPanel: {
      control: 'boolean',
      description: 'Whether history panel is visible'
    },
    hasMemory: {
      control: 'boolean',
      description: 'Whether user has memory data'
    },
    memoryCount: {
      control: 'number',
      description: 'Number of memory items'
    }
  }
}

export default meta
type Story = StoryObj<typeof ChatControls>

export const SearchMode: Story = {
  args: {
    mode: 'search',
    showHistoryPanel: false,
    hasMemory: false,
    memoryCount: 0
  }
}

export const AskMode: Story = {
  args: {
    mode: 'ask',
    showHistoryPanel: false,
    hasMemory: false,
    memoryCount: 0
  }
}

export const WithMemory: Story = {
  args: {
    mode: 'search',
    showHistoryPanel: false,
    hasMemory: true,
    memoryCount: 15
  }
}

export const HistoryPanelOpen: Story = {
  args: {
    mode: 'ask',
    showHistoryPanel: true,
    hasMemory: true,
    memoryCount: 8
  }
}

export const FullFeatures: Story = {
  args: {
    mode: 'search',
    showHistoryPanel: false,
    hasMemory: true,
    memoryCount: 42
  }
}
