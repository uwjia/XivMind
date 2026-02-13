import ConfirmDialog from './ConfirmDialog.vue'

export default {
  title: 'Components/ConfirmDialog',
  component: ConfirmDialog,
  tags: ['autodocs'],
  argTypes: {
    visible: {
      control: 'boolean',
      description: 'Whether the dialog is visible'
    },
    title: {
      control: 'text',
      description: 'Dialog title'
    },
    message: {
      control: 'text',
      description: 'Dialog message content'
    },
    type: {
      control: 'select',
      description: 'Dialog type',
      options: ['danger', 'warning', 'info']
    },
    confirmText: {
      control: 'text',
      description: 'Confirm button text'
    },
    cancelText: {
      control: 'text',
      description: 'Cancel button text'
    }
  }
}

export const Danger = {
  args: {
    visible: true,
    title: 'Delete Download Task',
    message: 'Are you sure you want to delete this download task? This action cannot be undone.',
    type: 'danger',
    confirmText: 'Delete',
    cancelText: 'Cancel'
  }
}

export const Warning = {
  args: {
    visible: true,
    title: 'Remove Bookmark',
    message: 'Are you sure you want to remove this paper from your bookmarks?',
    type: 'warning',
    confirmText: 'Remove',
    cancelText: 'Keep'
  }
}

export const Info = {
  args: {
    visible: true,
    title: 'Confirm Action',
    message: 'Do you want to proceed with this action?',
    type: 'info',
    confirmText: 'Proceed',
    cancelText: 'Go Back'
  }
}

export const Hidden = {
  args: {
    visible: false,
    title: 'Hidden Dialog',
    message: 'This dialog is not visible.',
    type: 'info'
  }
}
