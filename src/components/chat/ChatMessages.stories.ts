import type { Meta, StoryObj } from '@storybook/vue3'
import ChatMessages from '@/components/chat/ChatMessages.vue'
import type { Message } from '@/composables/useChatMessages'

const meta: Meta<typeof ChatMessages> = {
  title: 'Components/Chat/ChatMessages',
  component: ChatMessages,
  tags: ['autodocs'],
  argTypes: {
    loading: {
      control: 'boolean',
      description: 'Loading state'
    }
  }
}

export default meta
type Story = StoryObj<typeof ChatMessages>

const mockMessages: Message[] = [
  {
    role: 'user',
    content: 'What are the key innovations in transformer architecture?'
  },
  {
    role: 'assistant',
    content: '**Key Innovations in Transformer Architecture:**\n\n1. **Self-Attention Mechanism** - Allows the model to weigh the importance of different parts of the input\n2. **Positional Encoding** - Provides position information without recurrence\n3. **Parallel Processing** - Enables faster training compared to RNNs',
    answer: '**Key Innovations in Transformer Architecture:**\n\n1. **Self-Attention Mechanism** - Allows the model to weigh the importance of different parts of the input\n2. **Positional Encoding** - Provides position information without recurrence\n3. **Parallel Processing** - Enables faster training compared to RNNs',
    references: [
      { id: '1706.03762', title: 'Attention Is All You Need', authors: ['Vaswani', 'Shazeer'], relevance_score: 0.95 }
    ]
  }
]

const mockPapersMessage: Message = {
  role: 'assistant',
  content: 'Found 3 papers',
  papers: [
    {
      id: '2301.12345',
      title: 'Attention Mechanisms in Deep Learning: A Survey',
      abstract: 'This paper provides a comprehensive survey of attention mechanisms in deep learning, covering various architectures and applications.',
      authors: ['John Smith', 'Jane Doe', 'Bob Johnson'],
      primary_category: 'cs.LG',
      categories: ['cs.LG', 'cs.AI'],
      published: '2024-01-15T10:00:00',
      similarity_score: 0.92
    },
    {
      id: '2301.12346',
      title: 'Transformer Architectures for Natural Language Processing',
      abstract: 'We present a detailed analysis of transformer architectures and their applications in NLP tasks.',
      authors: ['Alice Wang', 'Charlie Brown'],
      primary_category: 'cs.CL',
      categories: ['cs.CL', 'cs.LG'],
      published: '2024-01-10T08:30:00',
      similarity_score: 0.85
    }
  ],
  model: 'sentence-transformers'
}

const formatMessage = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const isCopied = () => false
const setMessageRef = () => {}

export const Empty: Story = {
  args: {
    messages: [],
    loading: false,
    isCopied,
    formatMessage,
    setMessageRef
  }
}

export const WithMessages: Story = {
  args: {
    messages: mockMessages,
    loading: false,
    isCopied,
    formatMessage,
    setMessageRef
  }
}

export const WithPapers: Story = {
  args: {
    messages: [mockMessages[0], mockPapersMessage],
    loading: false,
    isCopied,
    formatMessage,
    setMessageRef
  }
}

export const Loading: Story = {
  args: {
    messages: mockMessages,
    loading: true,
    isCopied,
    formatMessage,
    setMessageRef
  }
}

export const ConfigError: Story = {
  args: {
    messages: [
      {
        role: 'user',
        content: 'What is machine learning?'
      },
      {
        role: 'assistant',
        content: 'Error: LLM provider not configured',
        isConfigError: true
      }
    ],
    loading: false,
    isCopied,
    formatMessage,
    setMessageRef
  }
}

export const LongConversation: Story = {
  args: {
    messages: [
      { role: 'user', content: 'Hello, can you help me with research?' },
      { role: 'assistant', content: 'Of course! I can help you search for papers or answer questions about research topics. What would you like to know?' },
      { role: 'user', content: 'Tell me about graph neural networks' },
      { role: 'assistant', content: '**Graph Neural Networks (GNNs)** are a class of deep learning methods designed to operate on graph-structured data.\n\nKey concepts include:\n- **Node embeddings**\n- **Message passing**\n- **Graph pooling**', answer: '**Graph Neural Networks (GNNs)** are a class of deep learning methods designed to operate on graph-structured data.\n\nKey concepts include:\n- **Node embeddings**\n- **Message passing**\n- **Graph pooling**' },
      { role: 'user', content: 'What are the main applications?' },
      { role: 'assistant', content: 'GNNs are used in:\n1. **Social Network Analysis**\n2. **Drug Discovery**\n3. **Recommendation Systems**\n4. **Traffic Prediction**\n5. **Knowledge Graphs**' }
    ],
    loading: false,
    isCopied,
    formatMessage,
    setMessageRef
  }
}
