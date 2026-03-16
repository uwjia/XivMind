import type { Meta, StoryObj } from '@storybook/vue3'
import CreateFolderDialog from '@/components/desktop/CreateFolderDialog.vue'

const meta: Meta<typeof CreateFolderDialog> = {
  title: 'Components/Desktop/CreateFolderDialog',
  component: CreateFolderDialog,
  tags: ['autodocs'],
  argTypes: {
    visible: {
      control: 'boolean',
      description: 'Whether the dialog is visible'
    }
  }
}

export default meta
type Story = StoryObj<typeof CreateFolderDialog>

export const Default: Story = {
  args: {
    visible: false
  }
}

export const Visible: Story = {
  args: {
    visible: true
  }
}

export const Hidden: Story = {
  args: {
    visible: false
  }
}
