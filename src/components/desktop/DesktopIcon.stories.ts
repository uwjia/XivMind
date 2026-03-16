import type { Meta, StoryObj } from '@storybook/vue3'
import DesktopIcon from '@/components/desktop/DesktopIcon.vue'
import type { DesktopItem } from '@/types/desktop'
import type { DownloadTask } from '@/services/download'

const meta: Meta<typeof DesktopIcon> = {
  title: 'Components/Desktop/DesktopIcon',
  component: DesktopIcon,
  tags: ['autodocs'],
  argTypes: {
    item: {
      control: 'object',
      description: 'Desktop item to display'
    },
    isSelected: {
      control: 'boolean',
      description: 'Whether the icon is selected'
    },
    isDragging: {
      control: 'boolean',
      description: 'Whether the icon is being dragged'
    },
    isRenaming: {
      control: 'boolean',
      description: 'Whether the icon is in rename mode'
    }
  }
}

export default meta
type Story = StoryObj<typeof DesktopIcon>

const createDesktopItem = (overrides: Partial<DesktopItem> = {}): DesktopItem => ({
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

const createDownloadTask = (overrides: Partial<DownloadTask> = {}): DownloadTask => ({
  id: 'task-1',
  paper_id: '2301.07062',
  arxiv_id: '2301.07062',
  title: 'Attention Is All You Need: Transformer Architecture for Natural Language Processing',
  status: 'completed',
  progress: 100,
  created_at: '2024-01-15T10:30:00Z',
  file_size: 1024 * 1024 * 2.5,
  file_path: '/downloads/papers/2301.07062.pdf',
  pdf_url: 'https://arxiv.org/pdf/2301.07062v1',
  ...overrides
})

export const Default: Story = {
  args: {
    item: createDesktopItem(),
    task: createDownloadTask(),
    isSelected: false,
    isDragging: false,
    isRenaming: false
  }
}

export const Selected: Story = {
  args: {
    item: createDesktopItem(),
    task: createDownloadTask(),
    isSelected: true,
    isDragging: false,
    isRenaming: false
  }
}

export const Dragging: Story = {
  args: {
    item: createDesktopItem(),
    task: createDownloadTask(),
    isSelected: false,
    isDragging: true,
    isRenaming: false
  }
}

export const Renaming: Story = {
  args: {
    item: createDesktopItem(),
    task: createDownloadTask(),
    isSelected: true,
    isDragging: false,
    isRenaming: true
  }
}

export const WithLongName: Story = {
  args: {
    item: createDesktopItem({
      name: '2301.07062v2-very-long-paper-identifier'
    }),
    task: createDownloadTask(),
    isSelected: false,
    isDragging: false,
    isRenaming: false
  }
}

export const Downloading: Story = {
  args: {
    item: createDesktopItem(),
    task: createDownloadTask({
      status: 'downloading',
      progress: 65
    }),
    isSelected: false,
    isDragging: false,
    isRenaming: false
  }
}

export const Failed: Story = {
  args: {
    item: createDesktopItem(),
    task: createDownloadTask({
      status: 'failed',
      error_message: 'Connection timeout'
    }),
    isSelected: false,
    isDragging: false,
    isRenaming: false
  }
}
