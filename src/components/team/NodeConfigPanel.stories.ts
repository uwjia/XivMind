import NodeConfigPanel from '@/components/team/NodeConfigPanel.vue'

export default {
  title: 'Components/Team/NodeConfigPanel',
  component: NodeConfigPanel,
  tags: ['autodocs'],
  argTypes: {}
}

export const Empty = {
  render: () => ({
    components: { NodeConfigPanel },
    template: `
      <div style="width: 320px; height: 500px;">
        <NodeConfigPanel />
      </div>
    `
  })
}

export const Compact = {
  render: () => ({
    components: { NodeConfigPanel },
    template: `
      <div style="width: 280px; height: 400px;">
        <NodeConfigPanel />
      </div>
    `
  })
}

export const FullHeight = {
  render: () => ({
    components: { NodeConfigPanel },
    template: `
      <div style="width: 320px; height: 600px;">
        <NodeConfigPanel />
      </div>
    `
  })
}
