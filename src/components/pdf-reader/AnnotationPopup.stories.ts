import AnnotationPopup from '@/components/pdf-reader/AnnotationPopup.vue'
import type { Meta, StoryObj } from '@storybook/vue3'

const meta: Meta<typeof AnnotationPopup> = {
  title: 'PDF Reader/AnnotationPopup',
  component: AnnotationPopup,
  tags: ['autodocs'],
  argTypes: {
    position: {
      control: 'object',
      description: 'Popup position (x, y coordinates)'
    },
    selectedText: {
      control: 'text',
      description: 'Selected text content'
    }
  }
}

export default meta
type Story = StoryObj<typeof AnnotationPopup>

export const Default: Story = {
  args: {
    position: { x: 400, y: 200 },
    selectedText: 'This is a sample selected text from the PDF document.'
  }
}

export const ShortText: Story = {
  args: {
    position: { x: 300, y: 150 },
    selectedText: 'Short text'
  }
}

export const LongText: Story = {
  args: {
    position: { x: 500, y: 300 },
    selectedText: 'This is a much longer selected text that demonstrates how the popup handles longer content selections from the PDF document. It contains multiple sentences and should still display properly with the annotation tools available.'
  }
}

export const TopPosition: Story = {
  args: {
    position: { x: 400, y: 100 },
    selectedText: 'Text selected near the top of the page'
  }
}

export const BottomPosition: Story = {
  args: {
    position: { x: 400, y: 700 },
    selectedText: 'Text selected near the bottom of the page'
  }
}
