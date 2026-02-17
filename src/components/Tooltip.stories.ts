import Tooltip from './Tooltip.vue'

export default {
  title: 'Components/Tooltip',
  component: Tooltip,
  tags: ['autodocs'],
  argTypes: {
    content: {
      control: 'text',
      description: 'Tooltip content text'
    },
    position: {
      control: 'select',
      description: 'Tooltip position relative to trigger',
      options: ['top', 'bottom', 'left', 'right']
    },
    type: {
      control: 'select',
      description: 'Tooltip visual style',
      options: ['default', 'info', 'success', 'warning']
    },
    delay: {
      control: 'number',
      description: 'Delay before showing tooltip (ms)'
    }
  }
}

export const Default = {
  args: {
    content: 'Default tooltip',
    position: 'top',
    type: 'default',
    delay: 200
  },
  render: (args: any) => ({
    components: { Tooltip },
    setup() {
      return { args }
    },
    template: `
      <div style="padding: 60px; display: flex; justify-content: center; align-items: center;">
        <Tooltip v-bind="args">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">
            Hover me
          </button>
        </Tooltip>
      </div>
    `
  })
}

export const Info = {
  args: {
    content: 'Click to fetch papers',
    position: 'top',
    type: 'info',
    delay: 200
  },
  render: (args: any) => ({
    components: { Tooltip },
    setup() {
      return { args }
    },
    template: `
      <div style="padding: 60px; display: flex; justify-content: center; align-items: center;">
        <Tooltip v-bind="args">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">
            Hover me
          </button>
        </Tooltip>
      </div>
    `
  })
}

export const Success = {
  args: {
    content: '42 papers stored',
    position: 'top',
    type: 'success',
    delay: 200
  },
  render: (args: any) => ({
    components: { Tooltip },
    setup() {
      return { args }
    },
    template: `
      <div style="padding: 60px; display: flex; justify-content: center; align-items: center;">
        <Tooltip v-bind="args">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">
            Hover me
          </button>
        </Tooltip>
      </div>
    `
  })
}

export const Warning = {
  args: {
    content: 'Fetching papers...',
    position: 'top',
    type: 'warning',
    delay: 200
  },
  render: (args: any) => ({
    components: { Tooltip },
    setup() {
      return { args }
    },
    template: `
      <div style="padding: 60px; display: flex; justify-content: center; align-items: center;">
        <Tooltip v-bind="args">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">
            Hover me
          </button>
        </Tooltip>
      </div>
    `
  })
}

export const Positions = {
  render: () => ({
    components: { Tooltip },
    template: `
      <div style="padding: 100px; display: flex; justify-content: center; align-items: center; gap: 20px;">
        <Tooltip content="Top tooltip" position="top" type="info">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">Top</button>
        </Tooltip>
        <Tooltip content="Bottom tooltip" position="bottom" type="success">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">Bottom</button>
        </Tooltip>
        <Tooltip content="Left tooltip" position="left" type="warning">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">Left</button>
        </Tooltip>
        <Tooltip content="Right tooltip" position="right" type="default">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">Right</button>
        </Tooltip>
      </div>
    `
  })
}

export const AllTypes = {
  render: () => ({
    components: { Tooltip },
    template: `
      <div style="padding: 60px; display: flex; justify-content: center; align-items: center; gap: 16px;">
        <Tooltip content="Default style" type="default">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">Default</button>
        </Tooltip>
        <Tooltip content="Info style" type="info">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">Info</button>
        </Tooltip>
        <Tooltip content="Success style" type="success">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">Success</button>
        </Tooltip>
        <Tooltip content="Warning style" type="warning">
          <button style="padding: 12px 24px; border-radius: 8px; background: var(--bg-secondary); border: 1px solid var(--border-color); cursor: pointer;">Warning</button>
        </Tooltip>
      </div>
    `
  })
}
