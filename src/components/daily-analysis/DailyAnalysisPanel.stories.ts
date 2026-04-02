import DailyAnalysisPanel from '@/components/daily-analysis/DailyAnalysisPanel.vue'

export default {
  title: 'Components/DailyAnalysis/DailyAnalysisPanel',
  component: DailyAnalysisPanel,
  tags: ['autodocs'],
  argTypes: {
    date: {
      control: 'text',
      description: 'Selected date for analysis (YYYY-MM-DD format)'
    },
    userInterests: {
      control: 'array',
      description: 'User\'s research interests for recommendations'
    }
  }
}

export const Default = {
  args: {
    date: '2024-06-15',
    userInterests: ['Machine Learning', 'Computer Vision', 'NLP']
  }
}

export const WithoutInterests = {
  args: {
    date: '2024-06-15',
    userInterests: []
  }
}

export const WithManyInterests = {
  args: {
    date: '2024-06-15',
    userInterests: [
      'Machine Learning',
      'Computer Vision',
      'Natural Language Processing',
      'Reinforcement Learning',
      'Graph Neural Networks',
      'Medical Imaging',
      'Robotics'
    ]
  }
}

export const RecentDate = {
  args: {
    date: '2024-12-20',
    userInterests: ['AI', 'Deep Learning']
  }
}

export const OldDate = {
  args: {
    date: '2023-01-15',
    userInterests: ['Transformers', 'Attention Mechanisms']
  }
}
