import type { Meta, StoryObj } from '@storybook/vue3'
import DesktopFolder from '@/components/desktop/DesktopFolder.vue'
import type { DesktopItem } from '@/types/desktop'

const meta: Meta<typeof DesktopFolder> = {
  title: 'Components/Desktop/DesktopFolder',
  component: DesktopFolder,
  tags: ['autodocs'],
  argTypes: {
    item: {
      control: 'object',
      description: 'Folder item to display'
    },
    isRenaming: {
      control: 'boolean',
      description: 'Whether the folder is in rename mode'
    }
  },
  decorators: [
    (story) => ({
      components: { story },
      template: '<div style="width: 100px; height: 100px; position: relative;"><story /></div>'
    })
  ]
}

export default meta
type Story = StoryObj<typeof DesktopFolder>

const createFolderItem = (overrides: Partial<DesktopItem> = {}): DesktopItem => ({
  id: 'folder-1',
  type: 'folder',
  position: { x: 0, y: 0 },
  name: 'My Papers',
  children: ['item-1', 'item-2', 'item-3'],
  folderId: undefined,
  createdAt: '2024-01-15T10:30:00Z',
  updatedAt: '2024-01-15T10:30:00Z',
  ...overrides
})

export const Default: Story = {
  args: {
    item: createFolderItem(),
    isRenaming: false
  }
}

export const Renaming: Story = {
  args: {
    item: createFolderItem(),
    isRenaming: true
  }
}

export const EmptyFolder: Story = {
  args: {
    item: createFolderItem({
      children: []
    }),
    isRenaming: false
  }
}

export const WithManyItems: Story = {
  args: {
    item: createFolderItem({
      name: 'Important Papers',
      children: ['item-1', 'item-2', 'item-3', 'item-4', 'item-5', 'item-6', 'item-7', 'item-8', 'item-9', 'item-10']
    }),
    isRenaming: false
  }
}

export const LongName: Story = {
  args: {
    item: createFolderItem({
      name: 'Very Long Folder Name That Should Be Truncated'
    }),
    isRenaming: false
  }
}

export const NestedFolder: Story = {
  args: {
    item: createFolderItem({
      name: 'Subfolder',
      folderId: 'parent-folder-1'
    }),
    isRenaming: false
  }
}
