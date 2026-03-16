import type { Meta, StoryObj } from '@storybook/vue3'
import DesktopTooltip from '@/components/desktop/DesktopTooltip.vue'
import type { DesktopItem } from '@/types/desktop'
import type { DownloadTask } from '@/services/download'

const meta: Meta<typeof DesktopTooltip> = {
  title: 'Components/Desktop/DesktopTooltip',
  component: DesktopTooltip,
  tags: ['autodocs'],
  argTypes: {
    item: {
      control: 'object',
      description: 'Desktop item to show tooltip for'
    },
    task: {
      control: 'object',
      description: 'Download task associated with the item (for file items)'
    },
    position: {
      control: 'object',
      description: 'Position of the tooltip'
    }
  }
}

export default meta
type Story = StoryObj<typeof DesktopTooltip>

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
  children: ['item-1', 'item-2', 'item-3'],
  createdAt: '2024-01-15T10:30:00Z',
  updatedAt: '2024-01-15T10:30:00Z',
  ...overrides
})

const createDownloadTask = (overrides: Partial<DownloadTask> = {}): DownloadTask => ({
  id: 'task-1',
  paper_id: '2301.07062',
  arxiv_id: '2301.07062',
  title: 'Attention Is All You Need: Transformer Architecture for Natural Language Processing',
  status: 'completed',
  progress: 100,
  created_at: '2024-01-15T10:30:00Z',
  file_size: 1024 * 1024 * 2.5,
  file_path: '/Users/username/Downloads/papers/2301.07062.pdf',
  pdf_url: 'https://arxiv.org/pdf/2301.07062v1',
  ...overrides
})

export const FileTooltip: Story = {
  args: {
    item: createFileItem(),
    task: createDownloadTask(),
    position: { x: 120, y: 50 }
  }
}

export const FileTooltipDownloading: Story = {
  args: {
    item: createFileItem(),
    task: createDownloadTask({
      status: 'downloading',
      progress: 65
    }),
    position: { x: 120, y: 50 }
  }
}

export const FileTooltipFailed: Story = {
  args: {
    item: createFileItem(),
    task: createDownloadTask({
      status: 'failed',
      error_message: 'Connection timeout'
    }),
    position: { x: 120, y: 50 }
  }
}

export const FileTooltipPending: Story = {
  args: {
    item: createFileItem(),
    task: createDownloadTask({
      status: 'pending',
      progress: 0
    }),
    position: { x: 120, y: 50 }
  }
}

export const FolderTooltip: Story = {
  args: {
    item: createFolderItem(),
    position: { x: 120, y: 50 }
  }
}

export const FolderTooltipEmpty: Story = {
  args: {
    item: createFolderItem({
      children: []
    }),
    position: { x: 120, y: 50 }
  }
}

export const LongTitle: Story = {
  args: {
    item: createFileItem(),
    task: createDownloadTask({
      title: 'This is a very long paper title that should be truncated in the tooltip display to maintain a clean and readable interface for the user experience'
    }),
    position: { x: 120, y: 50 }
  }
}

export const LargeFileSize: Story = {
  args: {
    item: createFileItem(),
    task: createDownloadTask({
      file_size: 1024 * 1024 * 15.7
    }),
    position: { x: 120, y: 50 }
  }
}

export const LongFilePath: Story = {
  args: {
    item: createFileItem(),
    task: createDownloadTask({
      file_path: '/Users/username/Documents/Research/Papers/Very/Deep/Nested/Folder/Structure/2301.07062.pdf'
    }),
    position: { x: 120, y: 50 }
  }
}
