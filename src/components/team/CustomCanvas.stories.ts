import CustomCanvas from '@/components/team/CustomCanvas.vue'

export default {
  title: 'Components/Team/CustomCanvas',
  component: CustomCanvas,
  tags: ['autodocs'],
  argTypes: {}
}

export const Default = {
  render: () => ({
    components: { CustomCanvas },
    template: `
      <div style="width: 100%; height: 500px; background: var(--bg-secondary); border-radius: 8px; overflow: hidden;">
        <CustomCanvas />
      </div>
    `
  })
}

export const Compact = {
  render: () => ({
    components: { CustomCanvas },
    template: `
      <div style="width: 600px; height: 400px; background: var(--bg-secondary); border-radius: 8px; overflow: hidden;">
        <CustomCanvas />
      </div>
    `
  })
}
