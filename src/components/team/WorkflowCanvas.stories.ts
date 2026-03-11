import WorkflowCanvas from '@/components/team/WorkflowCanvas.vue'

export default {
  title: 'Components/Team/WorkflowCanvas',
  component: WorkflowCanvas,
  tags: ['autodocs'],
  argTypes: {}
}

export const Default = {
  render: () => ({
    components: { WorkflowCanvas },
    template: `
      <div style="width: 100%; height: 500px; background: var(--bg-secondary); border-radius: 8px; overflow: hidden;">
        <WorkflowCanvas />
      </div>
    `
  })
}

export const Compact = {
  render: () => ({
    components: { WorkflowCanvas },
    template: `
      <div style="width: 600px; height: 400px; background: var(--bg-secondary); border-radius: 8px; overflow: hidden;">
        <WorkflowCanvas />
      </div>
    `
  })
}
