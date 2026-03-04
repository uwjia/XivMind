import type { Meta, StoryObj } from '@storybook/vue3'
import { ArchivalMemoryEditor } from '@/components/memory'

const meta: Meta<typeof ArchivalMemoryEditor> = {
  title: 'Components/Memory/ArchivalMemoryEditor',
  component: ArchivalMemoryEditor,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#1a1a2e' },
        { name: 'light', value: '#f5f5f5' },
      ],
    },
  },
  decorators: [
    () => ({
      template: `
        <div style="display: flex; justify-content: center; align-items: center; min-height: 100vh; background: rgba(0,0,0,0.5);">
          <story />
        </div>
      `,
    }),
  ],
}

export default meta
type Story = StoryObj<typeof ArchivalMemoryEditor>

export const Default: Story = {
  args: {},
}

export const WithContent: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const titleInput = canvasElement.querySelector('input[placeholder="Enter note title..."]') as HTMLInputElement
    if (titleInput) {
      titleInput.value = 'Understanding Transformer Architecture'
      titleInput.dispatchEvent(new Event('input', { bubbles: true }))
    }
    
    const textarea = canvasElement.querySelector('textarea') as HTMLTextAreaElement
    if (textarea) {
      textarea.value = 'The transformer architecture uses self-attention mechanisms to process sequential data in parallel, unlike RNNs which process sequentially.'
      textarea.dispatchEvent(new Event('input', { bubbles: true }))
    }
  },
}

export const WithTags: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const tagInput = canvasElement.querySelector('input[placeholder="Add tag..."]') as HTMLInputElement
    if (tagInput) {
      tagInput.value = 'transformer'
      tagInput.dispatchEvent(new Event('input', { bubbles: true }))
      tagInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
      
      tagInput.value = 'attention'
      tagInput.dispatchEvent(new Event('input', { bubbles: true }))
      tagInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
      
      tagInput.value = 'deep-learning'
      tagInput.dispatchEvent(new Event('input', { bubbles: true }))
      tagInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
    }
  },
}

export const WithPapers: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const paperInput = canvasElement.querySelector('input[placeholder="e.g., 2301.12345"]') as HTMLInputElement
    if (paperInput) {
      paperInput.value = '2301.12345'
      paperInput.dispatchEvent(new Event('input', { bubbles: true }))
      paperInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
      
      paperInput.value = '2312.54321'
      paperInput.dispatchEvent(new Event('input', { bubbles: true }))
      paperInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
    }
  },
}

export const InsightType: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const select = canvasElement.querySelector('select') as HTMLSelectElement
    if (select) {
      select.value = 'insight'
      select.dispatchEvent(new Event('change', { bubbles: true }))
    }
    
    const titleInput = canvasElement.querySelector('input[placeholder="Enter note title..."]') as HTMLInputElement
    if (titleInput) {
      titleInput.value = 'Key Insight: Attention is All You Need'
      titleInput.dispatchEvent(new Event('input', { bubbles: true }))
    }
    
    const textarea = canvasElement.querySelector('textarea') as HTMLTextAreaElement
    if (textarea) {
      textarea.value = 'The key innovation of transformers is that they eliminate the need for recurrence and convolutions entirely, relying solely on attention mechanisms.'
      textarea.dispatchEvent(new Event('input', { bubbles: true }))
    }
  },
}

export const SummaryType: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const select = canvasElement.querySelector('select') as HTMLSelectElement
    if (select) {
      select.value = 'summary'
      select.dispatchEvent(new Event('change', { bubbles: true }))
    }
    
    const titleInput = canvasElement.querySelector('input[placeholder="Enter note title..."]') as HTMLInputElement
    if (titleInput) {
      titleInput.value = 'Summary: BERT Paper'
      titleInput.dispatchEvent(new Event('input', { bubbles: true }))
    }
    
    const textarea = canvasElement.querySelector('textarea') as HTMLTextAreaElement
    if (textarea) {
      textarea.value = 'BERT (Bidirectional Encoder Representations from Transformers) is a pre-training method that learns deep bidirectional representations by masking tokens and predicting them.'
      textarea.dispatchEvent(new Event('input', { bubbles: true }))
    }
  },
}

export const FullyFilled: Story = {
  args: {},
  play: async ({ canvasElement }) => {
    const titleInput = canvasElement.querySelector('input[placeholder="Enter note title..."]') as HTMLInputElement
    if (titleInput) {
      titleInput.value = 'Complete Research Note on Transformers'
      titleInput.dispatchEvent(new Event('input', { bubbles: true }))
    }
    
    const select = canvasElement.querySelector('select') as HTMLSelectElement
    if (select) {
      select.value = 'insight'
      select.dispatchEvent(new Event('change', { bubbles: true }))
    }
    
    const tagInput = canvasElement.querySelector('input[placeholder="Add tag..."]') as HTMLInputElement
    if (tagInput) {
      tagInput.value = 'transformer'
      tagInput.dispatchEvent(new Event('input', { bubbles: true }))
      tagInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
      
      tagInput.value = 'NLP'
      tagInput.dispatchEvent(new Event('input', { bubbles: true }))
      tagInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
    }
    
    const textarea = canvasElement.querySelector('textarea') as HTMLTextAreaElement
    if (textarea) {
      textarea.value = `# Transformer Architecture

## Key Components
- Self-attention mechanism
- Multi-head attention
- Positional encoding
- Layer normalization

## Benefits
- Parallel processing
- Long-range dependencies
- Scalability`
      textarea.dispatchEvent(new Event('input', { bubbles: true }))
    }
    
    const paperInput = canvasElement.querySelector('input[placeholder="e.g., 2301.12345"]') as HTMLInputElement
    if (paperInput) {
      paperInput.value = '1706.03762'
      paperInput.dispatchEvent(new Event('input', { bubbles: true }))
      paperInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
      
      paperInput.value = '1810.04805'
      paperInput.dispatchEvent(new Event('input', { bubbles: true }))
      paperInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
    }
  },
}

export const LightMode: Story = {
  parameters: {
    backgrounds: { default: 'light' },
  },
  args: {},
}
