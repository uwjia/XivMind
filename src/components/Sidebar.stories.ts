import Sidebar from './Sidebar.vue'

const mockSidebarStore = {
  isCollapsed: false,
  isMobileOpen: false,
  toggleSidebar: () => {},
  toggleMobileSidebar: () => {},
  closeMobileSidebar: () => {}
}

const mockThemeStore = {
  isDark: false,
  toggleTheme: () => {}
}

export default {
  title: 'Components/Sidebar',
  component: Sidebar,
  tags: ['autodocs'],
  argTypes: {
    isCollapsed: {
      control: 'boolean',
      description: 'Whether sidebar is collapsed'
    },
    isDark: {
      control: 'boolean',
      description: 'Whether dark mode is enabled'
    }
  }
}

export const Default = {
  args: {
    isCollapsed: false,
    isDark: false
  },
  parameters: {
    decorators: [
      (Story: any, context: { moduleParameters: any }) => {
        const { moduleParameters } = context
        moduleParameters.useSidebarStore = () => mockSidebarStore
        moduleParameters.useThemeStore = () => mockThemeStore
        return {
          component: Story,
          template: Story,
          moduleParameters
        }
      }
    ]
  }
}

export const Collapsed = {
  args: {
    isCollapsed: true,
    isDark: false
  },
  parameters: {
    decorators: [
      (Story: any, context: { moduleParameters: any }) => {
        const { moduleParameters } = context
        moduleParameters.useSidebarStore = () => mockSidebarStore
        moduleParameters.useThemeStore = () => mockThemeStore
        return {
          component: Story,
          template: Story,
          moduleParameters
        }
      }
    ]
  }
}
