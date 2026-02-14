import CategoryTree from './CategoryTree.vue'

export default {
  title: 'Components/CategoryTree',
  component: CategoryTree,
  tags: ['autodocs'],
  argTypes: {
    selectedCategory: {
      control: 'select',
      description: 'Currently selected category',
      options: ['cs*', 'cs.AI', 'cs.CV', 'cs.LG', 'cs.CL', 'other', null]
    },
    categoryCounts: {
      control: 'object',
      description: 'Object mapping category IDs to paper counts'
    }
  }
}

export const Default = {
  args: {
    selectedCategory: null,
    categoryCounts: {
      'cs.AI': 15,
      'cs.CV': 12,
      'cs.LG': 10,
      'cs.CL': 8,
      'cs.NE': 6,
      'cs.CR': 5,
      'cs.DC': 4,
      'cs.DB': 3,
      'cs.IR': 2,
      'cs.RO': 1,
      'math.CO': 3,
      'physics.comp-ph': 2
    }
  }
}

export const SelectedAI = {
  args: {
    selectedCategory: 'cs.AI',
    categoryCounts: {
      'cs.AI': 15,
      'cs.CV': 12,
      'cs.LG': 10,
      'cs.CL': 8,
      'cs.NE': 6,
      'cs.CR': 5
    }
  }
}

export const SelectedOther = {
  args: {
    selectedCategory: 'other',
    categoryCounts: {
      'cs.AI': 15,
      'cs.CV': 12,
      'cs.LG': 10,
      'math.CO': 5,
      'physics.comp-ph': 3,
      'stat.ML': 2
    }
  }
}

export const Empty = {
  args: {
    selectedCategory: null,
    categoryCounts: {}
  }
}

export const FewCategories = {
  args: {
    selectedCategory: null,
    categoryCounts: {
      'cs.AI': 3,
      'cs.LG': 2
    }
  }
}
