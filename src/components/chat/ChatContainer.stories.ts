import type { Meta, StoryObj } from '@storybook/vue3'
import ChatContainer from '@/components/chat/ChatContainer.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import type { Message } from '@/composables/useChatMessages'

const meta: Meta<typeof ChatContainer> = {
  title: 'Components/Chat/ChatContainer',
  component: ChatContainer,
  tags: ['autodocs'],
  argTypes: {
    mode: {
      control: 'select',
      options: ['search', 'ask'],
      description: 'Chat mode'
    },
    loading: {
      control: 'boolean',
      description: 'Loading state'
    }
  }
}

export default meta
type Story = StoryObj<typeof ChatContainer>

const mockMessages: Message[] = [
  {
    role: 'user',
    content: 'What are the key innovations in transformer architecture?'
  },
  {
    role: 'assistant',
    content: '**Key Innovations in Transformer Architecture:**\n\n1. **Self-Attention Mechanism** - Allows the model to weigh the importance of different parts of the input\n2. **Positional Encoding** - Provides position information without recurrence\n3. **Parallel Processing** - Enables faster training compared to RNNs',
    answer: '**Key Innovations in Transformer Architecture:**\n\n1. **Self-Attention Mechanism** - Allows the model to weigh the importance of different parts of the input\n2. **Positional Encoding** - Provides position information without recurrence\n3. **Parallel Processing** - Enables faster training compared to RNNs'
  }
]

const formatMessage = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const isCopied = () => false
const setMessageRef = () => {}

export const SearchModeEmpty: Story = {
  args: {
    mode: 'search',
    messages: [],
    loading: false,
    isCopied,
    formatMessage,
    setMessageRef
  }
}

export const AskModeEmpty: Story = {
  args: {
    mode: 'ask',
    messages: [],
    loading: false,
    isCopied,
    formatMessage,
    setMessageRef
  }
}

export const WithMessages: Story = {
  args: {
    mode: 'ask',
    messages: mockMessages,
    loading: false,
    isCopied,
    formatMessage,
    setMessageRef
  }
}

export const Loading: Story = {
  args: {
    mode: 'search',
    messages: mockMessages,
    loading: true,
    isCopied,
    formatMessage,
    setMessageRef
  }
}

export const WithInputSlot: Story = {
  args: {
    mode: 'ask',
    messages: mockMessages,
    loading: false,
    isCopied,
    formatMessage,
    setMessageRef
  },
  render: (args) => ({
    components: { ChatContainer, ChatInput },
    setup() {
      return { args }
    },
    template: `
      <div style="height: 500px; background: #1a1a2e; padding: 20px;">
        <ChatContainer v-bind="args">
          <template #input-area>
            <ChatInput 
              mode="ask" 
              :model-value="args.mode === 'ask' ? 'Type a question...' : 'Search query...'" 
            />
          </template>
        </ChatContainer>
      </div>
    `
  })
}
