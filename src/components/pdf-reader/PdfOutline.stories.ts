import PdfOutline from '@/components/pdf-reader/PdfOutline.vue'
import type { Meta, StoryObj } from '@storybook/vue3'
import type { PdfOutlineItem } from '@/types/pdf'

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

const nestedOutline: PdfOutlineItem[] = [
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
      },
      {
        title: '2.2 State of the Art',
        dest: 4,
        y: 100,
        items: [
          {
            title: '2.2.1 Transformer Models',
            dest: 4,
            y: 150,
            items: []
          },
          {
            title: '2.2.2 Large Language Models',
            dest: 4,
            y: 200,
            items: []
          }
        ]
      }
    ]
  }
]

const meta: Meta<typeof PdfOutline> = {
  title: 'PDF Reader/PdfOutline',
  component: PdfOutline,
  tags: ['autodocs'],
  argTypes: {
    outline: {
      control: 'object',
      description: 'PDF outline items'
    }
  }
}

export default meta
type Story = StoryObj<typeof PdfOutline>

export const Default: Story = {
  args: {
    outline: sampleOutline
  }
}

export const Empty: Story = {
  args: {
    outline: []
  }
}

export const Nested: Story = {
  args: {
    outline: nestedOutline
  }
}

export const SingleLevel: Story = {
  args: {
    outline: [
      { title: 'Abstract', dest: 1, y: 100, items: [] },
      { title: 'Introduction', dest: 1, y: 200, items: [] },
      { title: 'Methods', dest: 3, y: 100, items: [] },
      { title: 'Results', dest: 5, y: 100, items: [] },
      { title: 'Discussion', dest: 7, y: 100, items: [] },
      { title: 'Conclusion', dest: 9, y: 100, items: [] },
      { title: 'References', dest: 10, y: 100, items: [] }
    ]
  }
}

export const LongTitles: Story = {
  args: {
    outline: [
      { title: '1. Introduction and Background of the Research Study', dest: 1, y: 100, items: [] },
      { title: '2. Comprehensive Literature Review and Analysis', dest: 2, y: 100, items: [
        { title: '2.1 Overview of Existing Methodologies and Approaches', dest: 2, y: 150, items: [] },
        { title: '2.2 Critical Analysis of Previous Research Findings', dest: 2, y: 200, items: [] }
      ]},
      { title: '3. Proposed Methodology and Implementation Details', dest: 4, y: 100, items: [] }
    ]
  }
}
