import type { Meta, StoryObj } from '@storybook/vue3'
import ConversationHistoryPanel from '@/components/ConversationHistoryPanel.vue'
import { useConversationStore } from '@/stores/conversation-store'

const meta: Meta<typeof ConversationHistoryPanel> = {
  title: 'Components/ConversationHistoryPanel',
  component: ConversationHistoryPanel,
  tags: ['autodocs'],
  argTypes: {
    visible: {
      control: 'boolean',
      description: 'Whether the panel is visible'
    },
    triggerElement: {
      control: false,
      description: 'The trigger element for positioning'
    }
  },
  parameters: {
    layout: 'fullscreen'
  }
}

export default meta
type Story = StoryObj<typeof ConversationHistoryPanel>

const mockConversations = [
  {
    session_id: 'conv-1',
    user_id: 'default',
    title: 'Search for machine learning papers',
    mode: 'search',
    created_at: '2024-01-15T10:30:00',
    updated_at: '2024-01-15T14:20:00',
    starred: true,
    pinned: true,
    message_count: 12
  },
  {
    session_id: 'conv-2',
    user_id: 'default',
    title: 'Ask about neural networks',
    mode: 'ask',
    created_at: '2024-01-14T09:00:00',
    updated_at: '2024-01-14T11:30:00',
    starred: false,
    pinned: false,
    message_count: 5
  },
  {
    session_id: 'conv-3',
    user_id: 'default',
    title: 'Ask about transformer architecture',
    mode: 'ask',
    created_at: '2024-01-13T16:45:00',
    updated_at: '2024-01-13T17:00:00',
    starred: true,
    pinned: false,
    message_count: 3
  },
  {
    session_id: 'conv-4',
    user_id: 'default',
    title: 'Search for transformer architecture',
    mode: 'search',
    created_at: '2024-01-12T08:00:00',
    updated_at: '2024-01-12T10:00:00',
    starred: false,
    pinned: false,
    message_count: 8
  }
]

function createMockStore() {
  const store = useConversationStore()
  store.conversations = mockConversations as any
  store.currentSessionId = 'conv-1'
  return store
}

export const Default: Story = {
  decorators: [
    () => ({
      setup() {
        createMockStore()
      },
      template: `
        <div style="padding: 20px; background: #1a1a2e; min-height: 100vh;">
          <div style="position: relative; width: 100%; height: 500px;">
            <story />
          </div>
        </div>
      `
    })
  ],
  args: {
    visible: true,
    triggerElement: null,
    onClose: () => {},
    onSelect: () => {}
  }
}

export const Hidden: Story = {
  decorators: [
    () => ({
      setup() {
        createMockStore()
      },
      template: `
        <div style="padding: 20px; background: #1a1a2e; min-height: 100vh;">
          <p style="color: #888;">Panel is hidden - click "Show panel" in controls to see it</p>
          <story />
        </div>
      `
    })
  ],
  args: {
    visible: false,
    triggerElement: null,
    onClose: () => {},
    onSelect: () => {}
  }
}

export const Empty: Story = {
  decorators: [
    () => ({
      setup() {
        const store = useConversationStore()
        store.conversations = []
        store.currentSessionId = ''
      },
      template: `
        <div style="padding: 20px; background: #1a1a2e; min-height: 100vh;">
          <div style="position: relative; width: 100%; height: 500px;">
            <story />
          </div>
        </div>
      `
    })
  ],
  args: {
    visible: true,
    triggerElement: null,
    onClose: () => {},
    onSelect: () => {}
  }
}

export const ManyItems: Story = {
  decorators: [
    () => ({
      setup() {
        const store = useConversationStore()
        const manyConversations = Array.from({ length: 20 }, (_, i) => ({
          session_id: `conv-${i + 1}`,
          user_id: 'default',
          title: `Conversation ${i + 1}: ${['Search', 'Ask'][i % 2]} mode discussion`,
          mode: ['search', 'ask'][i % 2],
          created_at: new Date(2024, 0, 15 - i).toISOString(),
          updated_at: new Date(2024, 0, 15 - i).toISOString(),
          starred: i % 4 === 0,
          pinned: i % 5 === 0,
          message_count: Math.floor(Math.random() * 20) + 1
        }))
        store.conversations = manyConversations as any
        store.currentSessionId = 'conv-1'
      },
      template: `
        <div style="padding: 20px; background: #1a1a2e; min-height: 100vh;">
          <div style="position: relative; width: 100%; height: 500px;">
            <story />
          </div>
        </div>
      `
    })
  ],
  args: {
    visible: true,
    triggerElement: null,
    onClose: () => {},
    onSelect: () => {}
  }
}
