import Sidebar from './Sidebar.vue'

const mockSidebarStore = {
  isCollapsed: () => false,
  isMobileOpen: () => false,
  isDatePickerOpen: () => false,
  isCategoryPickerOpen: () => false,
  toggleSidebar: () => {},
  toggleMobileSidebar: () => {},
  toggleDatePicker: () => {},
  toggleCategoryPicker: () => {},
  closeDatePicker: () => {},
  closeCategoryPicker: () => {}
}

const mockThemeStore = {
  isDark: () => false,
  toggleTheme: () => {}
}

const mockPaperStore = {
  selectedCategory: () => 'all',
  selectedDate: () => 'all',
  setSelectedCategory: () => {},
  setSelectedDate: () => {}
}

const mockConfigStore = {
  maxResults: () => 50
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
    },
    selectedCategory: {
      control: 'text',
      description: 'Currently selected category'
    },
    selectedDate: {
      control: 'text',
      description: 'Currently selected date filter'
    }
  }
}

export const Default = {
  args: {
    isCollapsed: false,
    isDark: false,
    selectedCategory: 'all',
    selectedDate: 'all'
  },
  parameters: {
    decorators: [
      (Story: any, context: { moduleParameters: any }) => {
        const { moduleParameters } = context
        moduleParameters.useSidebarStore = () => mockSidebarStore
        moduleParameters.useThemeStore = () => mockThemeStore
        moduleParameters.usePaperStore = () => mockPaperStore
        moduleParameters.useConfigStore = () => mockConfigStore
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
    isDark: false,
    selectedCategory: 'cs.AI',
    selectedDate: 'all'
  },
  parameters: {
    decorators: [
      (Story: any, context: { moduleParameters: any }) => {
        const { moduleParameters } = context
        moduleParameters.useSidebarStore = () => mockSidebarStore
        moduleParameters.useThemeStore = () => mockThemeStore
        moduleParameters.usePaperStore = () => mockPaperStore
        moduleParameters.useConfigStore = () => mockConfigStore
        return {
          component: Story,
          template: Story,
          moduleParameters
        }
      }
    ]
  }
}

export const WithCategory = {
  args: {
    isCollapsed: false,
    isDark: false,
    selectedCategory: 'cs.AI',
    selectedDate: 'all'
  },
  parameters: {
    decorators: [
      (Story: any, context: { moduleParameters: any }) => {
        const { moduleParameters } = context
        moduleParameters.useSidebarStore = () => mockSidebarStore
        moduleParameters.useThemeStore = () => mockThemeStore
        moduleParameters.usePaperStore = () => mockPaperStore
        moduleParameters.useConfigStore = () => mockConfigStore
        return {
          component: Story,
          template: Story,
          moduleParameters
        }
      }
    ]
  }
}