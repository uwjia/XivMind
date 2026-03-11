import TaskView from '@/components/team/TaskView.vue'

export default {
  title: 'Components/Team/TaskView',
  component: TaskView,
  tags: ['autodocs'],
  argTypes: {}
}

export const Default = {
  render: () => ({
    components: { TaskView },
    template: `
      <div style="max-width: 900px; margin: 0 auto; padding: 24px; background: var(--bg-primary); min-height: 100vh;">
        <TaskView />
      </div>
    `
  })
}

export const Compact = {
  render: () => ({
    components: { TaskView },
    template: `
      <div style="max-width: 700px; margin: 0 auto; padding: 16px; background: var(--bg-primary); min-height: 100vh;">
        <TaskView />
      </div>
    `
  })
}

export const WideLayout = {
  render: () => ({
    components: { TaskView },
    template: `
      <div style="max-width: 1200px; margin: 0 auto; padding: 24px; background: var(--bg-primary); min-height: 100vh;">
        <TaskView />
      </div>
    `
  })
}
