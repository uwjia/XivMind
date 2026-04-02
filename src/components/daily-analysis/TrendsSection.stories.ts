import TrendsSection from '@/components/daily-analysis/TrendsSection.vue'
import type { Trend } from '@/types/dailyAnalysis'

export default {
  title: 'Components/DailyAnalysis/TrendsSection',
  component: TrendsSection,
  tags: ['autodocs'],
  argTypes: {
    trends: {
      control: 'object',
      description: 'List of research trends'
    }
  }
}

const defaultTrends: Trend[] = [
  {
    name: 'Vision Transformers',
    paper_count: 25,
    description: 'Growing interest in applying transformer architectures to computer vision tasks, achieving state-of-the-art results on image classification and object detection benchmarks.',
    paper_ids: ['2301.0001', '2301.0002', '2301.0003']
  },
  {
    name: 'Efficient Training Methods',
    paper_count: 18,
    description: 'Novel approaches to reduce computational costs and memory requirements during model training, including gradient checkpointing and mixed precision techniques.',
    paper_ids: ['2301.0004', '2301.0005']
  },
  {
    name: 'Multimodal Learning',
    paper_count: 15,
    description: 'Integration of visual, textual, and audio modalities for comprehensive understanding and generation tasks.',
    paper_ids: ['2301.0006', '2301.0007', '2301.0008']
  }
]

export const Default = {
  args: {
    trends: defaultTrends
  }
}

export const SingleTrend = {
  args: {
    trends: [
      {
        name: 'Large Language Models',
        paper_count: 42,
        description: 'Research focused on scaling laws, efficient inference, and applications of large language models across various domains.',
        paper_ids: ['2301.0009', '2301.0010', '2301.0011', '2301.0012']
      }
    ]
  }
}

export const ManyTrends = {
  args: {
    trends: [
      {
        name: 'Diffusion Models',
        paper_count: 30,
        description: 'Generative models based on diffusion processes for high-quality image synthesis.',
        paper_ids: ['2301.0013', '2301.0014']
      },
      {
        name: 'Neural Architecture Search',
        paper_count: 12,
        description: 'Automated methods for discovering optimal neural network architectures.',
        paper_ids: ['2301.0015']
      },
      {
        name: 'Federated Learning',
        paper_count: 8,
        description: 'Distributed machine learning approaches preserving data privacy.',
        paper_ids: ['2301.0016', '2301.0017']
      },
      {
        name: 'Graph Neural Networks',
        paper_count: 22,
        description: 'Deep learning on graph-structured data for molecular and social network analysis.',
        paper_ids: ['2301.0018', '2301.0019', '2301.0020']
      },
      {
        name: 'Self-Supervised Learning',
        paper_count: 19,
        description: 'Learning representations from unlabeled data through pretext tasks.',
        paper_ids: ['2301.0021', '2301.0022']
      }
    ]
  }
}

export const EmptyTrends = {
  args: {
    trends: []
  }
}
