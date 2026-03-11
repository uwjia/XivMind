import WorkflowEditor from '@/components/team/WorkflowEditor.vue'

export default {
  title: 'Components/Team/WorkflowEditor',
  component: WorkflowEditor,
  tags: ['autodocs'],
  argTypes: {
    activeView: {
      control: 'select',
      options: ['task', 'workflow'],
      description: 'Currently active view'
    }
  }
}

export const Default = {
  args: {
    activeView: 'workflow'
  }
}

export const TaskView = {
  args: {
    activeView: 'task'
  }
}

export const FullWidth = {
  render: () => ({
    components: { WorkflowEditor },
    template: `
      <div style="width: 100%; height: 600px; background: var(--bg-primary);">
        <WorkflowEditor active-view="workflow" />
      </div>
    `
  })
}

export const Compact = {
  render: () => ({
    components: { WorkflowEditor },
    template: `
      <div style="width: 800px; height: 500px; background: var(--bg-primary);">
        <WorkflowEditor active-view="workflow" />
      </div>
    `
  })
}
