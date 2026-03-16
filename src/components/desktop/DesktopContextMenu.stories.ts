import type { Meta, StoryObj } from '@storybook/vue3'
import DesktopContextMenu from '@/components/desktop/DesktopContextMenu.vue'
import type { ContextMenuTarget, DesktopItem } from '@/types/desktop'

const meta: Meta<typeof DesktopContextMenu> = {
  title: 'Components/Desktop/DesktopContextMenu',
  component: DesktopContextMenu,
  tags: ['autodocs'],
  argTypes: {
    position: {
      control: 'object',
      description: 'Position of the context menu'
    },
    target: {
      control: 'object',
      description: 'Target of the context menu (desktop, file, or folder)'
    },
    selectedCount: {
      control: 'number',
      description: 'Number of selected items'
    },
    hasClipboard: {
      control: 'boolean',
      description: 'Whether there are items in clipboard'
    }
  },
  decorators: [
    (story) => ({
      components: { story },
      template: '<div style="width: 400px; height: 400px; position: relative; background: #1a1a2e;"><story /></div>'
    })
  ]
}

export default meta
type Story = StoryObj<typeof DesktopContextMenu>

const createFileItem = (overrides: Partial<DesktopItem> = {}): DesktopItem => ({
  id: 'desktop-1',
  type: 'file',
  position: { x: 0, y: 0 },
  name: '2301.07062',
  taskId: 'task-1',
  folderId: undefined,
  createdAt: '2024-01-15T10:30:00Z',
  updatedAt: '2024-01-15T10:30:00Z',
  ...overrides
})

const createFolderItem = (overrides: Partial<DesktopItem> = {}): DesktopItem => ({
  id: 'folder-1',
  type: 'folder',
  position: { x: 0, y: 0 },
  name: 'My Papers',
  children: ['item-1', 'item-2'],
  createdAt: '2024-01-15T10:30:00Z',
  updatedAt: '2024-01-15T10:30:00Z',
  ...overrides
})

export const DesktopContext: Story = {
  args: {
    position: { x: 100, y: 100 },
    target: { type: 'desktop' },
    selectedCount: 0,
    hasClipboard: false
  }
}

export const DesktopWithClipboard: Story = {
  args: {
    position: { x: 100, y: 100 },
    target: { type: 'desktop' },
    selectedCount: 0,
    hasClipboard: true
  }
}

export const DesktopWithSelection: Story = {
  args: {
    position: { x: 100, y: 100 },
    target: { type: 'desktop' },
    selectedCount: 3,
    selectedItems: [
      createFileItem(),
      createFileItem({ id: 'desktop-2', name: '2301.07063' }),
      createFileItem({ id: 'desktop-3', name: '2301.07064' })
    ],
    hasClipboard: false
  }
}

export const FileContext: Story = {
  args: {
    position: { x: 150, y: 150 },
    target: { type: 'file', item: createFileItem() },
    selectedCount: 1,
    hasClipboard: false
  }
}

export const FolderContext: Story = {
  args: {
    position: { x: 200, y: 200 },
    target: { type: 'folder', item: createFolderItem() },
    selectedCount: 1,
    hasClipboard: false
  }
}

export const MultipleSelection: Story = {
  args: {
    position: { x: 100, y: 100 },
    target: { type: 'desktop' },
    selectedCount: 5,
    selectedItems: [
      createFileItem(),
      createFileItem({ id: 'desktop-2', name: '2301.07063' }),
      createFileItem({ id: 'desktop-3', name: '2301.07064' }),
      createFolderItem(),
      createFolderItem({ id: 'folder-2', name: 'Archive' })
    ],
    hasClipboard: false
  }
}
