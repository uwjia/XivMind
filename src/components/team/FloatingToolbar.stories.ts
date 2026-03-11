import FloatingToolbar from '@/components/team/FloatingToolbar.vue'

export default {
  title: 'Components/Team/FloatingToolbar',
  component: FloatingToolbar,
  tags: ['autodocs'],
  argTypes: {
    activeView: {
      control: 'select',
      options: ['task', 'workflow'],
      description: 'Currently active view'
    },
    loading: {
      control: 'boolean',
      description: 'Show loading spinner on refresh button'
    }
  }
}

export const TaskView = {
  args: {
    activeView: 'task'
  }
}

export const WorkflowView = {
  args: {
    activeView: 'workflow'
  }
}

export const Loading = {
  args: {
    activeView: 'workflow',
    loading: true
  }
}

export const AllStates = {
  render: () => ({
    components: { FloatingToolbar },
    template: `
      <div style="display: flex; gap: 24px; flex-wrap: wrap;">
        <div style="position: relative; width: 60px; height: 120px; background: var(--bg-secondary); border-radius: 10px;">
          <FloatingToolbar active-view="task" style="position: relative;" />
          <p style="position: absolute; bottom: -30px; left: 0; font-size: 12px; color: var(--text-muted);">Task Active</p>
        </div>
        <div style="position: relative; width: 60px; height: 120px; background: var(--bg-secondary); border-radius: 10px;">
          <FloatingToolbar active-view="workflow" style="position: relative;" />
          <p style="position: absolute; bottom: -30px; left: 0; font-size: 12px; color: var(--text-muted);">Workflow Active</p>
        </div>
        <div style="position: relative; width: 60px; height: 120px; background: var(--bg-secondary); border-radius: 10px;">
          <FloatingToolbar active-view="workflow" :loading="true" style="position: relative;" />
          <p style="position: absolute; bottom: -30px; left: 0; font-size: 12px; color: var(--text-muted);">Loading</p>
        </div>
      </div>
    `
  })
}
