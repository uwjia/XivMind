import Toast from './Toast.vue'

export default {
  title: 'Components/Toast',
  component: Toast,
  tags: ['autodocs'],
  argTypes: {
    visible: {
      control: 'boolean',
      description: 'Whether to toast is visible'
    },
    message: {
      control: 'text',
      description: 'Toast message content'
    },
    type: {
      control: 'select',
      description: 'Toast type',
      options: ['success', 'error', 'warning', 'info']
    }
  }
}

export const Success = {
  args: {
    visible: true,
    message: 'Operation completed successfully!',
    type: 'success'
  }
}

export const Error = {
  args: {
    visible: true,
    message: 'An error occurred. Please try again.',
    type: 'error'
  }
}

export const Warning = {
  args: {
    visible: true,
    message: 'This is a warning message.',
    type: 'warning'
  }
}

export const Info = {
  args: {
    visible: true,
    message: 'This is an informational message.',
    type: 'info'
  }
}