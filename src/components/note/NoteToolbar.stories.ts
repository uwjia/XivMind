import type { Meta, StoryObj } from '@storybook/vue3'
import NoteToolbar from '@/components/note/NoteToolbar.vue'

const meta: Meta<typeof NoteToolbar> = {
  title: 'Components/Note/NoteToolbar',
  component: NoteToolbar,
  tags: ['autodocs'],
  argTypes: {
    searchQuery: {
      control: 'text',
      description: 'Current search query'
    },
    filterTag: {
      control: 'text',
      description: 'Currently selected filter tag'
    },
    allTags: {
      control: 'object',
      description: 'All available tags'
    },
    selectedCount: {
      control: 'number',
      description: 'Number of selected notes'
    }
  }
}

export default meta
type Story = StoryObj<typeof NoteToolbar>

export const Default: Story = {
  args: {
    searchQuery: '',
    filterTag: null,
    allTags: ['transformer', 'attention', 'NLP', 'research'],
    selectedCount: 0
  }
}

export const WithSearchQuery: Story = {
  args: {
    searchQuery: 'transformer attention',
    filterTag: null,
    allTags: ['transformer', 'attention', 'NLP', 'research'],
    selectedCount: 0
  }
}

export const WithFilterTag: Story = {
  args: {
    searchQuery: '',
    filterTag: 'transformer',
    allTags: ['transformer', 'attention', 'NLP', 'research'],
    selectedCount: 0
  }
}

export const WithSelectedNotes: Story = {
  args: {
    searchQuery: '',
    filterTag: null,
    allTags: ['transformer', 'attention', 'NLP', 'research'],
    selectedCount: 3
  }
}

export const WithSearchAndSelection: Story = {
  args: {
    searchQuery: 'attention',
    filterTag: 'NLP',
    allTags: ['transformer', 'attention', 'NLP', 'research'],
    selectedCount: 5
  }
}

export const NoTags: Story = {
  args: {
    searchQuery: '',
    filterTag: null,
    allTags: [],
    selectedCount: 0
  }
}

export const ManyTags: Story = {
  args: {
    searchQuery: '',
    filterTag: null,
    allTags: [
      'transformer',
      'attention',
      'NLP',
      'research',
      'deep-learning',
      'neural-network',
      'BERT',
      'GPT',
      'LLM',
      'fine-tuning'
    ],
    selectedCount: 0
  }
}

export const ManySelected: Story = {
  args: {
    searchQuery: '',
    filterTag: null,
    allTags: ['transformer', 'attention', 'NLP'],
    selectedCount: 15
  }
}

export const ComplexState: Story = {
  args: {
    searchQuery: 'self-attention mechanism',
    filterTag: 'transformer',
    allTags: ['transformer', 'attention', 'NLP', 'research', 'deep-learning'],
    selectedCount: 7
  }
}
