import HighValueSection from '@/components/daily-analysis/HighValueSection.vue'
import type { HighValuePaper } from '@/types/dailyAnalysis'

export default {
  title: 'Components/DailyAnalysis/HighValueSection',
  component: HighValueSection,
  tags: ['autodocs'],
  argTypes: {
    papers: {
      control: 'object',
      description: 'List of high-value papers'
    },
    streamingPapers: {
      control: 'object',
      description: 'List of streaming papers (real-time analysis results)'
    }
  }
}

const defaultPapers: HighValuePaper[] = [
  {
    paper_id: '2406.04619',
    title: 'Attention Is All You Need: Scalable Object Detection with Transformers',
    innovation_type: 'novel_method',
    innovation_description: 'Introduces a novel transformer-based architecture for object detection that eliminates the need for hand-designed components like anchor boxes and non-maximum suppression.',
    confidence: 0.95
  },
  {
    paper_id: '2406.05234',
    title: 'Efficient Fine-Tuning of Large Language Models with Low-Rank Adaptation',
    innovation_type: 'significant_improvement',
    innovation_description: 'Proposes a parameter-efficient fine-tuning method that reduces memory requirements by 10x while maintaining comparable performance to full fine-tuning.',
    confidence: 0.88
  },
  {
    paper_id: '2406.03891',
    title: 'Cross-Domain Transfer Learning for Medical Image Analysis',
    innovation_type: 'cross_domain',
    innovation_description: 'Demonstrates successful transfer of vision models from natural images to medical imaging, achieving state-of-the-art results on multiple diagnostic tasks.',
    confidence: 0.82
  }
]

const streamingPapers = [
  {
    paper_id: '2406.06123',
    title: 'Novel Attention Mechanism for Long-Context Understanding',
    innovation_type: 'novel_method',
    innovation_description: 'Introduces a sparse attention pattern that enables processing of sequences up to 100K tokens efficiently.',
    confidence: 0.92
  },
  {
    paper_id: '2406.05987',
    title: 'Benchmarking Large Language Models on Scientific Reasoning',
    innovation_type: 'new_problem',
    innovation_description: 'Creates a comprehensive benchmark for evaluating LLM capabilities on scientific problem-solving tasks.',
    confidence: 0.78
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

export const HighConfidence = {
  args: {
    papers: [
      {
        paper_id: '2406.07000',
        title: 'Breakthrough in Quantum Machine Learning',
        innovation_type: 'novel_method',
        innovation_description: 'First practical demonstration of quantum advantage for machine learning tasks on real quantum hardware.',
        confidence: 0.98
      }
    ]
  }
}

export const LowConfidence = {
  args: {
    papers: [
      {
        paper_id: '2406.07001',
        title: 'Preliminary Study on Emerging Techniques',
        innovation_type: 'new_problem',
        innovation_description: 'Initial exploration of a new research direction with promising but preliminary results.',
        confidence: 0.72
      }
    ]
  }
}

export const Empty = {
  args: {
    papers: []
  }
}
