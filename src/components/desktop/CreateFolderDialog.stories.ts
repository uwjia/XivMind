import type { Meta, StoryObj } from '@storybook/vue3'
import CreateFolderDialog from '@/components/desktop/CreateFolderDialog.vue'

const meta: Meta<typeof CreateFolderDialog> = {
  title: 'Components/Desktop/CreateFolderDialog',
  component: CreateFolderDialog,
  tags: ['autodocs']
}

export default meta
type Story = StoryObj<typeof CreateFolderDialog>

export const Default: Story = {
  args: {}
}

export const Visible: Story = {
  args: {}
}

export const Hidden: Story = {
  args: {}
}
