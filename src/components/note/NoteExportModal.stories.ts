import type { Meta, StoryObj } from '@storybook/vue3'
import NoteExportModal from '@/components/note/NoteExportModal.vue'
import type { Note } from '@/types/note'

const sampleNotes: Note[] = [
  {
    id: 'note-1',
    content: 'Transformer architecture uses self-attention mechanisms to process sequential data in parallel.',
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-15T10:30:00Z',
    tags: ['transformer', 'attention'],
    source: 'Attention Is All You Need'
  },
  {
    id: 'note-2',
    content: 'BERT uses bidirectional training to understand context from both directions.',
    createdAt: '2024-01-16T14:20:00Z',
    updatedAt: '2024-01-16T14:20:00Z',
    tags: ['BERT', 'NLP'],
    source: 'BERT: Pre-training of Deep Bidirectional Transformers'
  },
  {
    id: 'note-3',
    content: 'GPT-3 demonstrates emergent abilities at scale, showing capabilities not explicitly trained for.',
    createdAt: '2024-01-17T09:15:00Z',
    updatedAt: '2024-01-17T09:15:00Z',
    tags: ['GPT', 'LLM', 'emergent-abilities'],
    source: 'Language Models are Few-Shot Learners'
  }
]

const meta: Meta<typeof NoteExportModal> = {
  title: 'Components/Note/NoteExportModal',
  component: NoteExportModal,
  tags: ['autodocs'],
  argTypes: {
    visible: {
      control: 'boolean',
      description: 'Modal visibility'
    },
    notes: {
      control: 'object',
      description: 'Array of notes to export'
    }
  }
}

export default meta
type Story = StoryObj<typeof NoteExportModal>

export const Default: Story = {
  args: {
    visible: true,
    notes: sampleNotes
  }
}

export const Hidden: Story = {
  args: {
    visible: false,
    notes: sampleNotes
  }
}

export const EmptyNotes: Story = {
  args: {
    visible: true,
    notes: []
  }
}

export const SingleNote: Story = {
  args: {
    visible: true,
    notes: [sampleNotes[0]]
  }
}

export const ManyNotes: Story = {
  args: {
    visible: true,
    notes: [
      ...sampleNotes,
      {
        id: 'note-4',
        content: 'Vision Transformer (ViT) applies transformer architecture to image classification tasks.',
        createdAt: '2024-01-18T11:00:00Z',
        updatedAt: '2024-01-18T11:00:00Z',
        tags: ['ViT', 'computer-vision'],
        source: 'An Image is Worth 16x16 Words'
      },
      {
        id: 'note-5',
        content: 'LoRA enables efficient fine-tuning of large language models with minimal parameters.',
        createdAt: '2024-01-19T16:45:00Z',
        updatedAt: '2024-01-19T16:45:00Z',
        tags: ['LoRA', 'fine-tuning', 'LLM'],
        source: 'LoRA: Low-Rank Adaptation of Large Language Models'
      }
    ]
  }
}

export const LongContentNotes: Story = {
  args: {
    visible: true,
    notes: [
      {
        id: 'note-long',
        content: `This is a very long note content that tests how the export modal handles longer text. It contains multiple sentences and demonstrates the text wrapping and preview functionality.

The note includes:
- Multiple paragraphs
- Various key points
- Detailed explanations

This helps ensure the export functionality works correctly with longer content.`,
        createdAt: '2024-01-20T08:00:00Z',
        updatedAt: '2024-01-20T08:00:00Z',
        tags: ['long-content', 'test'],
        source: 'Test Paper with Long Title That Should Be Truncated in the Preview'
      }
    ]
  }
}
