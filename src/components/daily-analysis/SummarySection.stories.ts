import SummarySection from '@/components/daily-analysis/SummarySection.vue'

export default {
  title: 'Components/DailyAnalysis/SummarySection',
  component: SummarySection,
  tags: ['autodocs'],
  argTypes: {
    summary: {
      control: 'text',
      description: 'Daily summary text'
    },
    themes: {
      control: 'array',
      description: 'List of main themes'
    }
  }
}

export const Default = {
  args: {
    summary: 'Today\'s arXiv papers show significant activity in machine learning and computer vision. Notable trends include transformer-based architectures for image classification, novel approaches to reinforcement learning, and advances in natural language processing for scientific literature.',
    themes: ['Transformers', 'Computer Vision', 'Reinforcement Learning', 'NLP']
  }
}

export const WithoutThemes = {
  args: {
    summary: 'A comprehensive analysis of today\'s papers reveals interesting patterns in deep learning research, with particular focus on efficient model architectures and training techniques.',
    themes: null
  }
}

export const ShortSummary = {
  args: {
    summary: 'Light activity day with 15 new papers in AI and ML.',
    themes: ['AI', 'ML']
  }
}

export const LongSummary = {
  args: {
    summary: 'Today marks a significant day in arXiv submissions with over 200 papers published across various domains. The machine learning community continues to push boundaries with innovative approaches to model efficiency and training dynamics. Computer vision research shows particular promise with several papers addressing real-world applications in medical imaging and autonomous systems. Natural language processing maintains its momentum with advances in large language models and their applications to scientific discovery. The intersection of reinforcement learning and robotics presents exciting new possibilities for embodied AI systems. Additionally, theoretical foundations continue to be strengthened with rigorous analysis of optimization methods and generalization bounds.',
    themes: ['Machine Learning', 'Computer Vision', 'NLP', 'Reinforcement Learning', 'Robotics', 'Theory']
  }
}
