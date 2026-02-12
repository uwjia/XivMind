import Header from './Header.vue'

export default {
  title: 'Components/Header',
  component: Header,
  tags: ['autodocs'],
  argTypes: {
    isCollapsed: {
      control: 'boolean',
      description: 'Whether to sidebar is collapsed'
    }
  }
}

export const Default = {
  args: {
    isCollapsed: false
  }
}

export const Collapsed = {
  args: {
    isCollapsed: true
  }
}
