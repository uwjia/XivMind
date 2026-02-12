import DatePicker from './DatePicker.vue'

const mockSetSelectedDate = () => {}

export default {
  title: 'Components/DatePicker',
  component: DatePicker,
  tags: ['autodocs'],
  argTypes: {
    isOpen: {
      control: 'boolean',
      description: 'Whether date picker is open'
    },
    modelValue: {
      control: 'text',
      description: 'Currently selected date value'
    }
  }
}

export const Default = {
  args: {
    isOpen: true,
    modelValue: 'all'
  },
  parameters: {
    decorators: [
      (Story: any, context: { moduleParameters: any }) => {
        const { moduleParameters } = context
        moduleParameters.usePaperStore = () => ({
          setSelectedDate: mockSetSelectedDate
        })
        return {
          component: Story,
          template: Story,
          moduleParameters
        }
      }
    ]
  }
}

export const WithDate = {
  args: {
    isOpen: true,
    modelValue: '2024-06-01'
  },
  parameters: {
    decorators: [
      (Story: any, context: { moduleParameters: any }) => {
        const { moduleParameters } = context
        moduleParameters.usePaperStore = () => ({
          setSelectedDate: mockSetSelectedDate
        })
        return {
          component: Story,
          template: Story,
          moduleParameters
        }
      }
    ]
  }
}