import CategoryPicker from './CategoryPicker.vue'

export default {
  title: 'Components/CategoryPicker',
  component: CategoryPicker,
  tags: ['autodocs'],
  argTypes: {
    isOpen: {
      control: 'boolean',
      description: 'Whether to category picker is open'
    },
    modelValue: {
      control: 'text',
      description: 'Currently selected category'
    }
  }
}

export const Default = {
  args: {
    isOpen: true,
    modelValue: 'all'
  }
}

export const WithCategory = {
  args: {
    isOpen: true,
    modelValue: 'cs.AI'
  }
}