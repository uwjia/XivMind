import type { Meta, StoryObj } from '@storybook/vue3'
import ChatInput from './ChatInput.vue'

const meta: Meta<typeof ChatInput> = {
  title: 'Components/Chat/ChatInput',
  component: ChatInput,
  tags: ['autodocs'],
  argTypes: {
    mode: {
      control: 'select',
      options: ['search', 'ask'],
      description: 'Chat mode'
    },
    modelValue: {
      control: 'text',
      description: 'Input value'
    },
    loading: {
      control: 'boolean',
      description: 'Loading state'
    }
  }
}

export default meta
type Story = StoryObj<typeof ChatInput>

export const SearchMode: Story = {
  args: {
    mode: 'search',
    modelValue: '',
    loading: false
  }
}

export const AskMode: Story = {
  args: {
    mode: 'ask',
    modelValue: '',
    loading: false
  }
}

export const WithText: Story = {
  args: {
    mode: 'search',
    modelValue: 'transformer attention mechanisms',
    loading: false
  }
}

export const Loading: Story = {
  args: {
    mode: 'ask',
    modelValue: 'What is machine learning?',
    loading: true
  }
}

export const LongText: Story = {
  args: {
    mode: 'ask',
    modelValue: 'This is a very long text that demonstrates how the input handles multiple lines of content. The textarea should expand to accommodate the content while staying within the maximum height limit. Users can type long queries and the input will resize automatically.',
    loading: false
  }
}
