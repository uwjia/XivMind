import ExecutionInputDialog from '@/components/team/ExecutionInputDialog.vue'

export default {
  title: 'Components/Team/ExecutionInputDialog',
  component: ExecutionInputDialog,
  tags: ['autodocs'],
  argTypes: {
    defaultInstruction: {
      control: 'text',
      description: 'Default instruction text'
    },
    defaultPaperIds: {
      control: 'object',
      description: 'Default paper IDs array'
    }
  }
}

export const Default = {
  args: {}
}

export const WithDefaultInstruction = {
  args: {
    defaultInstruction: 'Summarize the key findings of this paper and compare with related work.'
  }
}

export const WithPaperIds = {
  args: {
    defaultInstruction: 'Analyze these papers',
    defaultPaperIds: ['2401.12345', '2401.67890']
  }
}

export const FullyPopulated = {
  args: {
    defaultInstruction: 'Compare the attention mechanisms in Vision Transformers and BERT, focusing on computational efficiency and accuracy trade-offs.',
    defaultPaperIds: ['2301.00001', '2301.00002', '2301.00003']
  }
}
