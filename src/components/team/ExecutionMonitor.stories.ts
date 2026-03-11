import ExecutionMonitor from '@/components/team/ExecutionMonitor.vue'

export default {
  title: 'Components/Team/ExecutionMonitor',
  component: ExecutionMonitor,
  tags: ['autodocs'],
  argTypes: {
    showLogs: {
      control: 'boolean',
      description: 'Whether to show the logs section'
    },
    showOutput: {
      control: 'boolean',
      description: 'Whether to show the output section'
    }
  }
}

export const Default = {
  args: {
    showLogs: true,
    showOutput: true
  }
}

export const WithoutLogs = {
  args: {
    showLogs: false,
    showOutput: true
  }
}

export const WithoutOutput = {
  args: {
    showLogs: true,
    showOutput: false
  }
}

export const Minimal = {
  args: {
    showLogs: false,
    showOutput: false
  }
}

export const Compact = {
  render: () => ({
    components: { ExecutionMonitor },
    template: `
      <div style="width: 300px;">
        <ExecutionMonitor :show-logs="true" :show-output="true" />
      </div>
    `
  })
}

export const FullWidth = {
  render: () => ({
    components: { ExecutionMonitor },
    template: `
      <div style="width: 100%; max-width: 600px;">
        <ExecutionMonitor :show-logs="true" :show-output="true" />
      </div>
    `
  })
}
