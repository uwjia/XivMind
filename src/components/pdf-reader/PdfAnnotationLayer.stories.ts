import PdfAnnotationLayer from '@/components/pdf-reader/PdfAnnotationLayer.vue'
import type { Meta, StoryObj } from '@storybook/vue3'
import type { PdfAnnotation } from '@/types/pdf'

const sampleAnnotations: PdfAnnotation[] = [
  {
    id: '1',
    paper_id: 'paper-1',
    type: 'highlight',
    page_number: 1,
    position: { x: 100, y: 150, width: 200, height: 20 },
    color: 'rgba(255, 235, 59, 0.4)',
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z'
  },
  {
    id: '2',
    paper_id: 'paper-1',
    type: 'highlight',
    page_number: 1,
    position: { x: 100, y: 200, width: 150, height: 20 },
    color: 'rgba(33, 150, 243, 0.4)',
    created_at: '2024-01-15T10:05:00Z',
    updated_at: '2024-01-15T10:05:00Z'
  },
  {
    id: '3',
    paper_id: 'paper-1',
    type: 'underline',
    page_number: 1,
    position: { x: 100, y: 250, width: 180, height: 20 },
    color: '#4CAF50',
    created_at: '2024-01-15T10:10:00Z',
    updated_at: '2024-01-15T10:10:00Z'
  },
  {
    id: '4',
    paper_id: 'paper-1',
    type: 'comment',
    page_number: 1,
    position: { x: 0, y: 300, width: 24, height: 24 },
    color: '#FFC107',
    content: 'This is an important point that needs further investigation.',
    created_at: '2024-01-15T10:15:00Z',
    updated_at: '2024-01-15T10:15:00Z'
  },
  {
    id: '5',
    paper_id: 'paper-1',
    type: 'drawing',
    page_number: 1,
    position: { x: 100, y: 350, width: 100, height: 50 },
    color: '#E91E63',
    content: JSON.stringify([
      { x: 100, y: 350 },
      { x: 120, y: 360 },
      { x: 140, y: 355 },
      { x: 160, y: 370 },
      { x: 180, y: 365 },
      { x: 200, y: 380 }
    ]),
    stroke_width: 3,
    created_at: '2024-01-15T10:20:00Z',
    updated_at: '2024-01-15T10:20:00Z'
  }
]

const meta: Meta<typeof PdfAnnotationLayer> = {
  title: 'PDF Reader/PdfAnnotationLayer',
  component: PdfAnnotationLayer,
  tags: ['autodocs'],
  argTypes: {
    pageNumber: {
      control: { type: 'number', min: 1 },
      description: 'Page number'
    },
    annotations: {
      control: 'object',
      description: 'List of annotations'
    },
    zoom: {
      control: { type: 'range', min: 0.5, max: 3, step: 0.25 },
      description: 'Zoom level'
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
    }
  }
}

export default meta
type Story = StoryObj<typeof PdfAnnotationLayer>

export const Default: Story = {
  args: {
    pageNumber: 1,
    annotations: sampleAnnotations,
    zoom: 1,
    currentTool: 'select',
    currentColor: 'yellow',
    strokeWidth: 2
  },
  decorators: [
    () => ({
      template: `<div style="width: 600px; height: 500px; position: relative; background: #f5f5f5; border: 1px solid #ddd;">
        <story />
      </div>`
    })
  ]
}

export const Empty: Story = {
  args: {
    pageNumber: 1,
    annotations: [],
    zoom: 1,
    currentTool: 'select',
    currentColor: 'yellow',
    strokeWidth: 2
  },
  decorators: [
    () => ({
      template: `<div style="width: 600px; height: 500px; position: relative; background: #f5f5f5; border: 1px solid #ddd;">
        <story />
      </div>`
    })
  ]
}

export const HighlightMode: Story = {
  args: {
    pageNumber: 1,
    annotations: sampleAnnotations,
    zoom: 1,
    currentTool: 'highlight',
    currentColor: 'blue',
    strokeWidth: 2
  },
  decorators: [
    () => ({
      template: `<div style="width: 600px; height: 500px; position: relative; background: #f5f5f5; border: 1px solid #ddd;">
        <story />
      </div>`
    })
  ]
}

export const DrawingMode: Story = {
  args: {
    pageNumber: 1,
    annotations: sampleAnnotations,
    zoom: 1,
    currentTool: 'drawing',
    currentColor: 'pink',
    strokeWidth: 4
  },
  decorators: [
    () => ({
      template: `<div style="width: 600px; height: 500px; position: relative; background: #f5f5f5; border: 1px solid #ddd;">
        <story />
      </div>`
    })
  ]
}

export const ZoomedIn: Story = {
  args: {
    pageNumber: 1,
    annotations: sampleAnnotations,
    zoom: 1.5,
    currentTool: 'select',
    currentColor: 'yellow',
    strokeWidth: 2
  },
  decorators: [
    () => ({
      template: `<div style="width: 600px; height: 500px; position: relative; background: #f5f5f5; border: 1px solid #ddd; overflow: auto;">
        <story />
      </div>`
    })
  ]
}

export const OnlyHighlights: Story = {
  args: {
    pageNumber: 1,
    annotations: sampleAnnotations.filter(a => a.type === 'highlight'),
    zoom: 1,
    currentTool: 'select',
    currentColor: 'yellow',
    strokeWidth: 2
  },
  decorators: [
    () => ({
      template: `<div style="width: 600px; height: 500px; position: relative; background: #f5f5f5; border: 1px solid #ddd;">
        <story />
      </div>`
    })
  ]
}

export const OnlyComments: Story = {
  args: {
    pageNumber: 1,
    annotations: sampleAnnotations.filter(a => a.type === 'comment'),
    zoom: 1,
    currentTool: 'select',
    currentColor: 'yellow',
    strokeWidth: 2
  },
  decorators: [
    () => ({
      template: `<div style="width: 600px; height: 500px; position: relative; background: #f5f5f5; border: 1px solid #ddd;">
        <story />
      </div>`
    })
  ]
}
