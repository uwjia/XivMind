import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import NotePanel from '@/components/note/NotePanel.vue'

const meta: Meta<typeof NotePanel> = {
  title: 'Components/Note/NotePanel',
  component: NotePanel,
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
type Story = StoryObj<typeof NotePanel>

const MockStore = {
  notes: ref([
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
      tags: ['GPT', 'LLM'],
      source: 'Language Models are Few-Shot Learners'
    }
  ]),
  position: ref({ x: 100, y: 80 }),
  size: ref({ width: 340, height: 450 }),
  isMinimized: ref(false),
  isVisible: ref(true),
  selectedIds: ref<string[]>([]),
  filterTag: ref<string | null>(null),
  searchQuery: ref(''),
  hasUserMovedPanel: ref(false),
  noteBtnPosition: ref({ x: 0, y: 0 }),
  allTags: ref(['transformer', 'attention', 'BERT', 'NLP', 'GPT', 'LLM']),
  filteredNotes: ref([
    {
      id: 'note-1',
      content: 'Transformer architecture uses self-attention mechanisms.',
      createdAt: '2024-01-15T10:30:00Z',
      updatedAt: '2024-01-15T10:30:00Z',
      tags: ['transformer', 'attention'],
      source: 'Attention Is All You Need'
    },
    {
      id: 'note-2',
      content: 'BERT uses bidirectional training.',
      createdAt: '2024-01-16T14:20:00Z',
      updatedAt: '2024-01-16T14:20:00Z',
      tags: ['BERT', 'NLP'],
      source: 'BERT Paper'
    }
  ])
}

export const Default: Story = {
  render: () => ({
    components: { NotePanel },
    setup() {
      return {}
    },
    template: '<NotePanel />'
  })
}

export const Hidden: Story = {
  render: () => ({
    components: { NotePanel },
    setup() {
      MockStore.isVisible.value = false
      return {}
    },
    template: '<NotePanel />'
  })
}

export const Minimized: Story = {
  render: () => ({
    components: { NotePanel },
    setup() {
      MockStore.isVisible.value = true
      MockStore.isMinimized.value = true
      return {}
    },
    template: '<NotePanel />'
  })
}

export const WithSearchQuery: Story = {
  render: () => ({
    components: { NotePanel },
    setup() {
      MockStore.isMinimized.value = false
      MockStore.searchQuery.value = 'transformer'
      return {}
    },
    template: '<NotePanel />'
  })
}

export const WithFilterTag: Story = {
  render: () => ({
    components: { NotePanel },
    setup() {
      MockStore.searchQuery.value = ''
      MockStore.filterTag.value = 'NLP'
      return {}
    },
    template: '<NotePanel />'
  })
}

export const WithSelectedNotes: Story = {
  render: () => ({
    components: { NotePanel },
    setup() {
      MockStore.filterTag.value = null
      MockStore.selectedIds.value = ['note-1', 'note-2']
      return {}
    },
    template: '<NotePanel />'
  })
}

export const EmptyState: Story = {
  render: () => ({
    components: { NotePanel },
    setup() {
      MockStore.notes.value = []
      MockStore.filteredNotes.value = []
      MockStore.selectedIds.value = []
      return {}
    },
    template: '<NotePanel />'
  })
}

export const ManyNotes: Story = {
  render: () => ({
    components: { NotePanel },
    setup() {
      MockStore.notes.value = [
        ...MockStore.notes.value,
        {
          id: 'note-4',
          content: 'Vision Transformer applies transformer to images.',
          createdAt: '2024-01-18T11:00:00Z',
          updatedAt: '2024-01-18T11:00:00Z',
          tags: ['ViT', 'computer-vision'],
          source: 'An Image is Worth 16x16 Words'
        },
        {
          id: 'note-5',
          content: 'LoRA enables efficient fine-tuning.',
          createdAt: '2024-01-19T16:45:00Z',
          updatedAt: '2024-01-19T16:45:00Z',
          tags: ['LoRA', 'fine-tuning'],
          source: 'LoRA Paper'
        }
      ]
      return {}
    },
    template: '<NotePanel />'
  })
}
