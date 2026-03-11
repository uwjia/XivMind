import NodePreview from '@/components/team/NodePreview.vue'

export default {
  title: 'Components/Team/NodePreview',
  component: NodePreview,
  tags: ['autodocs'],
  argTypes: {
    result: {
      control: 'object',
      description: 'Result data to display'
    },
    error: {
      control: 'text',
      description: 'Error message to display'
    }
  }
}

export const TextResult = {
  args: {
    result: 'This is a sample text result from a node execution. It shows the output of the workflow step.'
  }
}

export const LongTextResult = {
  args: {
    result: 'This is a much longer text result that demonstrates how the component handles truncation. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
  }
}

export const ObjectResult = {
  args: {
    result: {
      status: 'success',
      data: {
        papers: 42,
        processed: 38,
        failed: 4
      },
      metadata: {
        duration: '2.5s',
        timestamp: '2024-01-15T10:30:00Z'
      }
    }
  }
}

export const ErrorResult = {
  args: {
    error: 'Failed to process the request: Connection timeout after 30 seconds'
  }
}

export const EmptyResult = {
  args: {
    result: null
  }
}

export const AllVariants = {
  render: () => ({
    components: { NodePreview },
    setup() {
      const results = [
        { title: 'Text Result', result: 'Simple text output' },
        { title: 'Object Result', result: { key: 'value', count: 10 } },
        { title: 'Error', error: 'Something went wrong' }
      ]
      return { results }
    },
    template: `
      <div style="display: flex; flex-direction: column; gap: 16px; max-width: 400px;">
        <div v-for="item in results" :key="item.title">
          <h4 style="margin-bottom: 8px; color: var(--text-secondary);">{{ item.title }}</h4>
          <NodePreview :result="item.result" :error="item.error" />
        </div>
      </div>
    `
  })
}
