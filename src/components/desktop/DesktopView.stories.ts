import type { Meta, StoryObj } from '@storybook/vue3'
import DesktopView from '@/components/desktop/DesktopView.vue'
import type { DownloadTask } from '@/services/download'

const meta: Meta<typeof DesktopView> = {
  title: 'Components/Desktop/DesktopView',
  component: DesktopView,
  tags: ['autodocs'],
  argTypes: {
    tasks: {
      control: 'object',
      description: 'List of download tasks to display on desktop'
    }
  },
  decorators: [
    (story) => ({
      components: { story },
      template: '<div style="width: 800px; height: 600px; background: #1a1a2e;"><story /></div>'
    })
  ]
}

export default meta
type Story = StoryObj<typeof DesktopView>

const createDownloadTask = (overrides: Partial<DownloadTask> = {}): DownloadTask => ({
  id: `task-${Math.random().toString(36).substr(2, 9)}`,
  paper_id: '2301.07062',
  arxiv_id: '2301.07062',
  title: 'Attention Is All You Need: Transformer Architecture for Natural Language Processing',
  status: 'completed',
  progress: 100,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  file_size: 1024 * 1024 * 2.5,
  file_path: '/downloads/papers/2301.07062.pdf',
  pdf_url: 'https://arxiv.org/pdf/2301.07062v1',
  ...overrides
})

const mockTasks: DownloadTask[] = [
  createDownloadTask({ id: 'task-1', paper_id: '2301.07062', arxiv_id: '2301.07062' }),
  createDownloadTask({ id: 'task-2', paper_id: '2301.07063', arxiv_id: '2301.07063' }),
  createDownloadTask({ id: 'task-3', paper_id: '2301.07064', arxiv_id: '2301.07064' }),
]

const manyTasks: DownloadTask[] = Array.from({ length: 15 }, (_, i) => 
  createDownloadTask({ 
    id: `task-${i}`,
    paper_id: `2301.0706${i}`,
    arxiv_id: `2301.0706${i}`,
    title: `Paper ${i + 1}: Research on Machine Learning and Artificial Intelligence`
  })
)

const downloadingTasks: DownloadTask[] = [
  createDownloadTask({ id: 'task-1', paper_id: '2301.07062', status: 'completed', progress: 100 }),
  createDownloadTask({ id: 'task-2', paper_id: '2301.07063', status: 'downloading', progress: 65 }),
  createDownloadTask({ id: 'task-3', paper_id: '2301.07064', status: 'downloading', progress: 30 }),
  createDownloadTask({ id: 'task-4', paper_id: '2301.07065', status: 'pending', progress: 0 }),
  createDownloadTask({ id: 'task-5', paper_id: '2301.07066', status: 'failed', error_message: 'Connection timeout' }),
]

export const Empty: Story = {
  args: {
    tasks: []
  }
}

export const WithTasks: Story = {
  args: {
    tasks: mockTasks
  }
}

export const ManyTasks: Story = {
  args: {
    tasks: manyTasks
  }
}

export const MixedStatus: Story = {
  args: {
    tasks: downloadingTasks
  }
}

export const SingleTask: Story = {
  args: {
    tasks: [createDownloadTask()]
  }
}
