import WorkflowTemplates from '@/components/team/WorkflowTemplates.vue'

export default {
  title: 'Components/Team/WorkflowTemplates',
  component: WorkflowTemplates,
  tags: ['autodocs'],
  argTypes: {}
}

export const Default = {
  render: () => ({
    components: { WorkflowTemplates },
    template: `
      <div style="position: relative; width: 100%; height: 600px; background: rgba(0,0,0,0.5);">
        <WorkflowTemplates />
      </div>
    `
  })
}

export const Compact = {
  render: () => ({
    components: { WorkflowTemplates },
    template: `
      <div style="position: relative; width: 100%; height: 400px; background: rgba(0,0,0,0.5);">
        <WorkflowTemplates style="width: 500px;" />
      </div>
    `
  })
}
