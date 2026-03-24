import PdfSidebar from '@/components/pdf-reader/PdfSidebar.vue'
import type { Meta, StoryObj } from '@storybook/vue3'
import type { PdfOutlineItem, PdfThumbnail } from '@/types/pdf'

const sampleOutline: PdfOutlineItem[] = [
  {
    title: 'Introduction',
    dest: 1,
    y: 100,
    items: []
  },
  {
    title: 'Related Work',
    dest: 3,
    y: 200,
    items: [
      {
        title: 'Deep Learning',
        dest: 3,
        y: 250,
        items: []
      },
      {
        title: 'Natural Language Processing',
        dest: 4,
        y: 300,
        items: []
      }
    ]
  },
  {
    title: 'Methodology',
    dest: 5,
    y: 100,
    items: [
      {
        title: 'Model Architecture',
        dest: 5,
        y: 150,
        items: []
      },
      {
        title: 'Training Procedure',
        dest: 6,
        y: 200,
        items: []
      }
    ]
  },
  {
    title: 'Experiments',
    dest: 8,
    y: 100,
    items: []
  },
  {
    title: 'Conclusion',
    dest: 12,
    y: 100,
    items: []
  }
]

const sampleThumbnails: PdfThumbnail[] = [
  { page_number: 1, src: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjE0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjE0MCIgZmlsbD0iI2ZmZiIvPjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1zaXplPSIxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+UGFnZSAxPC90ZXh0Pjwvc3ZnPg==', width: 100, height: 140 },
  { page_number: 2, src: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjE0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjE0MCIgZmlsbD0iI2ZmZiIvPjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1zaXplPSIxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+UGFnZSAyPC90ZXh0Pjwvc3ZnPg==', width: 100, height: 140 },
  { page_number: 3, src: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjE0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjE0MCIgZmlsbD0iI2ZmZiIvPjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1zaXplPSIxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+UGFnZSAzPC90ZXh0Pjwvc3ZnPg==', width: 100, height: 140 },
  { page_number: 4, src: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjE0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjE0MCIgZmlsbD0iI2ZmZiIvPjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1zaXplPSIxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+UGFnZSA0PC90ZXh0Pjwvc3ZnPg==', width: 100, height: 140 },
  { page_number: 5, src: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjE0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjE0MCIgZmlsbD0iI2ZmZiIvPjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1zaXplPSIxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+UGFnZSA1PC90ZXh0Pjwvc3ZnPg==', width: 100, height: 140 }
]

const meta: Meta<typeof PdfSidebar> = {
  title: 'PDF Reader/PdfSidebar',
  component: PdfSidebar,
  tags: ['autodocs'],
  argTypes: {
    outline: {
      control: 'object',
      description: 'PDF outline items'
    },
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
type Story = StoryObj<typeof PdfSidebar>

export const Default: Story = {
  args: {
    outline: sampleOutline,
    thumbnails: sampleThumbnails,
    currentPage: 1,
    loading: false
  }
}

export const EmptyOutline: Story = {
  args: {
    outline: [],
    thumbnails: sampleThumbnails,
    currentPage: 1,
    loading: false
  }
}

export const EmptyThumbnails: Story = {
  args: {
    outline: sampleOutline,
    thumbnails: [],
    currentPage: 1,
    loading: false
  }
}

export const Loading: Story = {
  args: {
    outline: [],
    thumbnails: [],
    currentPage: 1,
    loading: true
  }
}

export const MiddlePage: Story = {
  args: {
    outline: sampleOutline,
    thumbnails: sampleThumbnails,
    currentPage: 3,
    loading: false
  }
}

export const NestedOutline: Story = {
  args: {
    outline: [
      {
        title: 'Chapter 1: Introduction',
        dest: 1,
        y: 100,
        items: [
          {
            title: '1.1 Background',
            dest: 1,
            y: 200,
            items: [
              {
                title: '1.1.1 Motivation',
                dest: 1,
                y: 250,
                items: []
              },
              {
                title: '1.1.2 Objectives',
                dest: 1,
                y: 300,
                items: []
              }
            ]
          },
          {
            title: '1.2 Scope',
            dest: 2,
            y: 100,
            items: []
          }
        ]
      },
      {
        title: 'Chapter 2: Literature Review',
        dest: 3,
        y: 100,
        items: [
          {
            title: '2.1 Previous Work',
            dest: 3,
            y: 150,
            items: []
          }
        ]
      }
    ],
    thumbnails: sampleThumbnails,
    currentPage: 1,
    loading: false
  }
}
