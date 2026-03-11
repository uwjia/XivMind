import NodePalette from '@/components/team/NodePalette.vue'

export default {
  title: 'Components/Team/NodePalette',
  component: NodePalette,
  tags: ['autodocs'],
  argTypes: {}
}

export const Default = {
  render: () => ({
    components: { NodePalette },
    template: `
      <div style="width: 280px; height: 500px; background: var(--bg-primary); border-radius: 8px; overflow: hidden;">
        <NodePalette />
      </div>
    `
  })
}

export const Compact = {
  render: () => ({
    components: { NodePalette },
    template: `
      <div style="width: 240px; height: 400px; background: var(--bg-primary); border-radius: 8px; overflow: hidden;">
        <NodePalette />
      </div>
    `
  })
}
