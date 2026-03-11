import WorkflowToolbar from '@/components/team/WorkflowToolbar.vue'

export default {
  title: 'Components/Team/WorkflowToolbar',
  component: WorkflowToolbar,
  tags: ['autodocs'],
  argTypes: {
    leftDrawerCollapsed: {
      control: 'boolean',
      description: 'Whether the left drawer is collapsed'
    },
    rightDrawerCollapsed: {
      control: 'boolean',
      description: 'Whether the right drawer is collapsed'
    },
    showLogs: {
      control: 'boolean',
      description: 'Whether logs drawer is visible'
    },
    showOutput: {
      control: 'boolean',
      description: 'Whether output drawer is visible'
    }
  }
}

export const Default = {
  args: {
    leftDrawerCollapsed: false,
    rightDrawerCollapsed: false,
    showLogs: false,
    showOutput: false
  }
}

export const LeftDrawerCollapsed = {
  args: {
    leftDrawerCollapsed: true,
    rightDrawerCollapsed: false,
    showLogs: false,
    showOutput: false
  }
}

export const RightDrawerCollapsed = {
  args: {
    leftDrawerCollapsed: false,
    rightDrawerCollapsed: true,
    showLogs: false,
    showOutput: false
  }
}

export const BothDrawersCollapsed = {
  args: {
    leftDrawerCollapsed: true,
    rightDrawerCollapsed: true,
    showLogs: false,
    showOutput: false
  }
}

export const WithLogsVisible = {
  args: {
    leftDrawerCollapsed: false,
    rightDrawerCollapsed: false,
    showLogs: true,
    showOutput: false
  }
}

export const WithOutputVisible = {
  args: {
    leftDrawerCollapsed: false,
    rightDrawerCollapsed: false,
    showLogs: false,
    showOutput: true
  }
}

export const AllDrawersOpen = {
  args: {
    leftDrawerCollapsed: false,
    rightDrawerCollapsed: false,
    showLogs: true,
    showOutput: true
  }
}
