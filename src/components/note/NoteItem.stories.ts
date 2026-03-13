import type { Meta, StoryObj } from '@storybook/vue3'
import NoteItem from '@/components/note/NoteItem.vue'
import type { Note } from '@/types/note'

const meta: Meta<typeof NoteItem> = {
  title: 'Components/Note/NoteItem',
  component: NoteItem,
  tags: ['autodocs'],
  argTypes: {
    note: {
      control: 'object',
      description: 'Note object to display'
    },
    selected: {
      control: 'boolean',
      description: 'Whether the note is selected'
    }
  }
}

export default meta
type Story = StoryObj<typeof NoteItem>

const createNote = (overrides: Partial<Note> = {}): Note => ({
  id: 'note-1',
  content: 'Transformer architecture uses self-attention mechanisms to process sequential data in parallel.',
  createdAt: '2024-01-15T10:30:00Z',
  updatedAt: '2024-01-15T10:30:00Z',
  tags: ['transformer', 'attention'],
  ...overrides
})

export const Default: Story = {
  args: {
    note: createNote(),
    selected: false
  }
}

export const Selected: Story = {
  args: {
    note: createNote(),
    selected: true
  }
}

export const WithSource: Story = {
  args: {
    note: createNote({
      source: 'Attention Is All You Need'
    }),
    selected: false
  }
}

export const WithColor: Story = {
  args: {
    note: createNote({
      color: '#00BCD4'
    }),
    selected: false
  }
}

export const WithManyTags: Story = {
  args: {
    note: createNote({
      tags: ['transformer', 'attention', 'NLP', 'deep-learning', 'research', 'important']
    }),
    selected: false
  }
}

export const NoTags: Story = {
  args: {
    note: createNote({
      tags: []
    }),
    selected: false
  }
}

export const LongContent: Story = {
  args: {
    note: createNote({
      content: `This is a very long note that demonstrates how the component handles longer text content. It contains multiple sentences and paragraphs to test the text wrapping and layout behavior.

Key points discussed:
1. Self-attention mechanism allows parallel processing
2. Positional encoding provides sequence order information
3. Multi-head attention captures different representation subspaces

The transformer architecture has revolutionized NLP and beyond.`
    }),
    selected: false
  }
}

export const RecentNote: Story = {
  args: {
    note: createNote({
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }),
    selected: false
  }
}

export const OldNote: Story = {
  args: {
    note: createNote({
      createdAt: '2023-01-15T10:30:00Z',
      updatedAt: '2023-01-15T10:30:00Z'
    }),
    selected: false
  }
}

export const CompleteNote: Story = {
  args: {
    note: createNote({
      content: 'BERT uses bidirectional training to understand context from both directions.',
      tags: ['BERT', 'NLP', 'pre-training'],
      source: 'BERT: Pre-training of Deep Bidirectional Transformers',
      color: '#8B5CF6'
    }),
    selected: true
  }
}
