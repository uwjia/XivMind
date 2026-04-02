import RecommendationsSection from '@/components/daily-analysis/RecommendationsSection.vue'
import type { RecommendedPaper } from '@/types/dailyAnalysis'

export default {
  title: 'Components/DailyAnalysis/RecommendationsSection',
  component: RecommendationsSection,
  tags: ['autodocs'],
  argTypes: {
    papers: {
      control: 'object',
      description: 'List of recommended papers'
    },
    streamingPapers: {
      control: 'object',
      description: 'List of streaming papers (real-time recommendation results)'
    }
  }
}

const defaultPapers: RecommendedPaper[] = [
  {
    paper_id: '2406.04619',
    title: 'Attention Mechanisms in Vision Transformers: A Comprehensive Survey',
    relevance_score: 95,
    matched_interests: ['Computer Vision', 'Transformers', 'Deep Learning'],
    reason: 'This survey directly addresses your research interest in vision transformers and provides a comprehensive overview of recent attention mechanisms.'
  },
  {
    paper_id: '2406.05234',
    title: 'Efficient Training of Large-Scale Neural Networks',
    relevance_score: 88,
    matched_interests: ['Machine Learning', 'Optimization'],
    reason: 'Highly relevant to your work on training efficiency, presenting novel optimization techniques for large-scale models.'
  },
  {
    paper_id: '2406.03891',
    title: 'Self-Supervised Learning for Medical Image Analysis',
    relevance_score: 82,
    matched_interests: ['Medical Imaging', 'Self-Supervised Learning'],
    reason: 'Aligns with your interest in medical imaging applications and self-supervised learning methods.'
  }
]

const streamingPapers = [
  {
    paper_id: '2406.06123',
    title: 'Multi-Modal Learning for Scientific Document Understanding',
    relevance_score: 91,
    matched_interests: ['NLP', 'Multi-Modal Learning'],
    reason: 'Combines your interests in NLP and multi-modal learning for scientific document analysis.'
  },
  {
    paper_id: '2406.05987',
    title: 'Graph Neural Networks for Molecular Property Prediction',
    relevance_score: 79,
    matched_interests: ['Graph Neural Networks', 'Drug Discovery'],
    reason: 'Applies GNNs to molecular property prediction, relevant to your drug discovery research.'
  }
]

export const Default = {
  args: {
    papers: defaultPapers
  }
}

export const WithStreamingResults = {
  args: {
    papers: defaultPapers,
    streamingPapers: streamingPapers
  }
}

export const OnlyStreamingResults = {
  args: {
    papers: [],
    streamingPapers: streamingPapers
  }
}

export const HighRelevance = {
  args: {
    papers: [
      {
        paper_id: '2406.07000',
        title: 'Perfect Match: Direct Application of Your Research Interests',
        relevance_score: 98,
        matched_interests: ['Computer Vision', 'Transformers', 'Deep Learning', 'Medical Imaging'],
        reason: 'This paper directly combines all your primary research interests in a novel and impactful way.'
      }
    ]
  }
}

export const LowRelevance = {
  args: {
    papers: [
      {
        paper_id: '2406.07001',
        title: 'Tangentially Related Research',
        relevance_score: 65,
        matched_interests: ['Machine Learning'],
        reason: 'Contains some relevant methodology but applied to a different domain.'
      }
    ]
  }
}

export const ManyMatches = {
  args: {
    papers: [
      {
        paper_id: '2406.08001',
        title: 'Comprehensive Multi-Interest Paper',
        relevance_score: 92,
        matched_interests: ['Computer Vision', 'NLP', 'Transformers', 'Deep Learning', 'Medical Imaging', 'Graph Neural Networks'],
        reason: 'Interdisciplinary paper that spans multiple areas of your research interests.'
      }
    ]
  }
}

export const Empty = {
  args: {
    papers: []
  }
}
