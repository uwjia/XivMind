import PdfToolbar from '@/components/pdf-reader/PdfToolbar.vue'
import type { Meta, StoryObj } from '@storybook/vue3'

const meta: Meta<typeof PdfToolbar> = {
  title: 'PDF Reader/PdfToolbar',
  component: PdfToolbar,
  tags: ['autodocs'],
  argTypes: {
    zoom: {
      control: { type: 'range', min: 0.25, max: 5, step: 0.25 },
      description: 'Current zoom level'
    },
    zoomPercentage: {
      control: { type: 'number' },
      description: 'Zoom percentage display'
    },
    viewMode: {
      control: 'select',
      options: ['single', 'continuous'],
      description: 'View mode'
    },
    currentPage: {
      control: { type: 'number', min: 1 },
      description: 'Current page number'
    },
    totalPages: {
      control: { type: 'number', min: 1 },
      description: 'Total pages'
    },
    loading: {
      control: 'boolean',
      description: 'Loading state'
    },
    canGoPrev: {
      control: 'boolean',
      description: 'Can navigate to previous page'
    },
    canGoNext: {
      control: 'boolean',
      description: 'Can navigate to next page'
    },
    currentTool: {
      control: 'select',
      options: ['select', 'highlight', 'drawing'],
      description: 'Current annotation tool'
    },
    currentColor: {
      control: 'select',
      options: ['yellow', 'green', 'blue', 'pink', 'purple'],
      description: 'Current highlight color'
    },
    strokeWidth: {
      control: { type: 'range', min: 1, max: 10, step: 1 },
      description: 'Drawing stroke width'
    },
    showSidebar: {
      control: 'boolean',
      description: 'Sidebar visibility'
    }
  }
}

export default meta
type Story = StoryObj<typeof PdfToolbar>

export const Default: Story = {
  args: {
    zoom: 1,
    zoomPercentage: 100,
    viewMode: 'continuous',
    currentPage: 1,
    totalPages: 10,
    loading: false,
    canGoPrev: false,
    canGoNext: true,
    currentTool: 'select',
    currentColor: 'yellow',
    strokeWidth: 2,
    showSidebar: true
  }
}

export const Loading: Story = {
  args: {
    zoom: 1,
    zoomPercentage: 100,
    viewMode: 'continuous',
    currentPage: 1,
    totalPages: 10,
    loading: true,
    canGoPrev: false,
    canGoNext: false,
    currentTool: 'select',
    currentColor: 'yellow',
    strokeWidth: 2,
    showSidebar: false
  }
}

export const MiddlePage: Story = {
  args: {
    zoom: 1.5,
    zoomPercentage: 150,
    viewMode: 'single',
    currentPage: 5,
    totalPages: 10,
    loading: false,
    canGoPrev: true,
    canGoNext: true,
    currentTool: 'select',
    currentColor: 'yellow',
    strokeWidth: 2,
    showSidebar: true
  }
}

export const HighlightMode: Story = {
  args: {
    zoom: 1,
    zoomPercentage: 100,
    viewMode: 'continuous',
    currentPage: 1,
    totalPages: 10,
    loading: false,
    canGoPrev: false,
    canGoNext: true,
    currentTool: 'highlight',
    currentColor: 'blue',
    strokeWidth: 2,
    showSidebar: false
  }
}

export const DrawingMode: Story = {
  args: {
    zoom: 1,
    zoomPercentage: 100,
    viewMode: 'continuous',
    currentPage: 1,
    totalPages: 10,
    loading: false,
    canGoPrev: false,
    canGoNext: true,
    currentTool: 'drawing',
    currentColor: 'pink',
    strokeWidth: 4,
    showSidebar: false
  }
}

export const ZoomedIn: Story = {
  args: {
    zoom: 2,
    zoomPercentage: 200,
    viewMode: 'continuous',
    currentPage: 3,
    totalPages: 10,
    loading: false,
    canGoPrev: true,
    canGoNext: true,
    currentTool: 'select',
    currentColor: 'yellow',
    strokeWidth: 2,
    showSidebar: true
  }
}
