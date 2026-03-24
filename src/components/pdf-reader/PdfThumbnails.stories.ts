import PdfThumbnails from '@/components/pdf-reader/PdfThumbnails.vue'
import type { Meta, StoryObj } from '@storybook/vue3'
import type { PdfThumbnail } from '@/types/pdf'

const sampleThumbnails: PdfThumbnail[] = Array.from({ length: 10 }, (_, i) => ({
  page_number: i + 1,
  src: `data:image/svg+xml;base64,${btoa(`<svg width="100" height="140" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="140" fill="#fff"/><rect x="10" y="10" width="80" height="10" fill="#eee"/><rect x="10" y="25" width="60" height="5" fill="#ddd"/><rect x="10" y="35" width="70" height="5" fill="#ddd"/><rect x="10" y="45" width="50" height="5" fill="#ddd"/><text x="50" y="120" font-size="12" text-anchor="middle" fill="#999">${i + 1}</text></svg>`)}`,
  width: 100,
  height: 140
}))

const meta: Meta<typeof PdfThumbnails> = {
  title: 'PDF Reader/PdfThumbnails',
  component: PdfThumbnails,
  tags: ['autodocs'],
  argTypes: {
    thumbnails: {
      control: 'object',
      description: 'PDF thumbnail images'
    },
    currentPage: {
      control: { type: 'number', min: 1 },
      description: 'Current page number'
    },
    loading: {
      control: 'boolean',
      description: 'Loading state'
    }
  }
}

export default meta
type Story = StoryObj<typeof PdfThumbnails>

export const Default: Story = {
  args: {
    thumbnails: sampleThumbnails,
    currentPage: 1,
    loading: false
  }
}

export const Empty: Story = {
  args: {
    thumbnails: [],
    currentPage: 1,
    loading: false
  }
}

export const Loading: Story = {
  args: {
    thumbnails: [],
    currentPage: 1,
    loading: true
  }
}

export const MiddlePage: Story = {
  args: {
    thumbnails: sampleThumbnails,
    currentPage: 5,
    loading: false
  }
}

export const LastPage: Story = {
  args: {
    thumbnails: sampleThumbnails,
    currentPage: 10,
    loading: false
  }
}

export const FewPages: Story = {
  args: {
    thumbnails: sampleThumbnails.slice(0, 3),
    currentPage: 2,
    loading: false
  }
}
