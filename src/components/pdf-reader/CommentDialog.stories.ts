import CommentDialog from '@/components/pdf-reader/CommentDialog.vue'
import type { Meta, StoryObj } from '@storybook/vue3'

const meta: Meta<typeof CommentDialog> = {
  title: 'PDF Reader/CommentDialog',
  component: CommentDialog,
  tags: ['autodocs'],
  argTypes: {
    position: {
      control: 'object',
      description: 'Dialog position (x, y coordinates)'
    },
    initialContent: {
      control: 'text',
      description: 'Initial comment content'
    }
  }
}

export default meta
type Story = StoryObj<typeof CommentDialog>

export const Default: Story = {
  args: {
    position: { x: 300, y: 200 },
    initialContent: ''
  }
}

export const WithInitialContent: Story = {
  args: {
    position: { x: 400, y: 300 },
    initialContent: 'This is a pre-filled comment that can be edited before saving.'
  }
}

export const LongInitialContent: Story = {
  args: {
    position: { x: 350, y: 250 },
    initialContent: 'This is a longer comment that contains multiple sentences and demonstrates how the dialog handles longer text content. The textarea should properly display and allow editing of this content.'
  }
}

export const TopLeftPosition: Story = {
  args: {
    position: { x: 50, y: 50 },
    initialContent: ''
  }
}

export const BottomRightPosition: Story = {
  args: {
    position: { x: 600, y: 500 },
    initialContent: 'Comment positioned at bottom right'
  }
}
