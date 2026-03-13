import type { Meta, StoryObj } from '@storybook/vue3'
import NoteEditor from '@/components/note/NoteEditor.vue'

const meta: Meta<typeof NoteEditor> = {
  title: 'Components/Note/NoteEditor',
  component: NoteEditor,
  tags: ['autodocs'],
  argTypes: {
    initialContent: {
      control: 'text',
      description: 'Initial note content'
    },
    initialTags: {
      control: 'object',
      description: 'Initial tags array'
    },
    isEditing: {
      control: 'boolean',
      description: 'Whether editing an existing note'
    }
  }
}

export default meta
type Story = StoryObj<typeof NoteEditor>

export const Default: Story = {
  args: {
    initialContent: '',
    initialTags: [],
    isEditing: false
  }
}

export const WithContent: Story = {
  args: {
    initialContent: 'This is a sample note about transformer architectures and their attention mechanisms.',
    initialTags: [],
    isEditing: false
  }
}

export const WithTags: Story = {
  args: {
    initialContent: 'Key findings from the paper on self-attention mechanisms.',
    initialTags: ['transformer', 'attention', 'research'],
    isEditing: false
  }
}

export const EditingMode: Story = {
  args: {
    initialContent: 'This note is being edited. The button shows "Update" instead of "Save".',
    initialTags: ['edit', 'update'],
    isEditing: true
  }
}

export const LongContent: Story = {
  args: {
    initialContent: `This is a longer note that demonstrates how the editor handles multiple paragraphs.

Key points:
1. Transformer architecture uses self-attention
2. BERT uses bidirectional training
3. GPT uses autoregressive generation

The attention mechanism allows the model to weigh the importance of different parts of the input sequence when making predictions.`,
    initialTags: ['transformer', 'NLP', 'deep-learning'],
    isEditing: false
  }
}

export const ManyTags: Story = {
  args: {
    initialContent: 'A note with many tags to test the tag input field.',
    initialTags: ['machine-learning', 'deep-learning', 'neural-network', 'transformer', 'attention', 'NLP', 'research'],
    isEditing: false
  }
}
